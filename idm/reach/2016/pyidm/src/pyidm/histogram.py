from pathlib import Path

import pandas as pd
import numpy as np
import awkward as ak
import hist
import uproot

from . import rate
from .load import FromROOT
from .mfsa.accumulator import to_accumulator, from_accumulator


def _load_signal(fp: Path):
    plist = fp.stem.split('_')[:-1]
    params = {plist[i]: plist[i+1] for i in range(0, len(plist), 2)}
    for k in ['mchi', 'rmap', 'rdmchi']:
        params[k] = float(params[k])
    params['nruns'] = int(params['nruns'])
    nevents = params['nevents']
    if nevents[-1] == 'k':
        nevents = 1000*int(nevents[:-1])
    elif nevents[-1] == 'M':
        nevents = 1000000*int(nevents[:-1])
    else:
        nevents = int(nevents)
    params['nevents'] = nevents
    params['chi2_width_per_eps2'] = rate.rate(params['mchi'], params['rdmchi'], params['rmap'])
    params['ap_prod_rate_per_eps2'] = rate.darkphoton_production(params['rmap']*params['mchi'])
    return params, FromROOT.hps_reco()(fp)


def _load_bkgd(fp: Path):
    plist = fp.stem.split('_')[:-1]
    params = {plist[i]: plist[i+1] for i in range(1, len(plist)-1, 2)}
    params['name'] = plist[0]
    params['nruns'] = int(params['nruns'])
    return params, FromROOT.hps_reco()(fp)


def load(fp: Path):
    if 'idm' in fp.stem:
        return _load_signal(fp)
    return _load_bkgd(fp)


def safe_divide(numerator: np.array, denominator: np.array, *, fill_value=np.nan):
    if isinstance(denominator, ak.Array):
        denominator = denominator.to_numpy()
    if isinstance(numerator, ak.Array):
        numerator = numerator.to_numpy()
    result = np.full(len(denominator), fill_value, dtype=denominator.dtype)
    result[denominator > 0] = numerator[denominator > 0] / denominator[denominator > 0]
    return result


def process(args):
    params, events = args
    event_sel = (
        ak.count(events.vertex.chi2, axis=1) == 1
    )
    vtx = ak.flatten(events[event_sel].vertex)

    vtx_sel = (
        (vtx.electron.track.time < 10)
        & (vtx.positron.track.time < 10)
        & (vtx.electron.goodness_pid < 10)
        & (vtx.positron.goodness_pid < 10)
        & (abs(vtx.electron.track.time - (vtx.electron.cluster.time - 43.0)) < 4)
        & (abs(vtx.positron.track.time - (vtx.positron.cluster.time - 43.0)) < 4)
        & (abs(vtx.electron.cluster.time - vtx.positron.cluster.time) < 1.45)
        & (safe_divide(vtx.electron.track.chi2, vtx.electron.track.ndf, fill_value=9000) < 15)
        & (safe_divide(vtx.positron.track.chi2, vtx.positron.track.ndf, fill_value=9000) < 15)
        & (vtx.electron.track.p.mag < 1.750)
        & (vtx.electron.track.p.mag > 0.400)
        & (vtx.positron.track.p.mag > 0.400)
    )

    vtx = vtx[vtx_sel]
    n_trks = ak.count(events[event_sel].track.chi2, axis=1)[vtx_sel]

    h = {}
    h['vtx'] = hist.Hist(
        hist.axis.Regular(
            130, -80, 180,
            name='vtxz',
            label='Vertex Z [mm]'
        )
    )
    h['vtx'].fill(vtx.pos.fZ)

    h['n_trks'] = hist.Hist(
        hist.axis.Regular(
            5, 0, 5,
            name='n_trks',
            label='Total Num Reco Tracks'
        )
    )
    h['n_trks'].fill(n_trks)

    if 'idm' in params:
        # assume signal and do readout-acceptance calculations
        chi2 = ak.flatten(
            events[event_sel].mc_particle[events[event_sel].mc_particle.pdg == 1000023]
        )[vtx_sel]
        df = pd.DataFrame({
            'eps2': np.logspace(-2, -6)
        })
        df['ctau'] = rate.ctau(params['chi2_width_per_eps2']*df.eps2)
        df['num_pass'] = ak.count(vtx.chi2)
        df['num_thrown'] = params['nevents']*params['nruns']

        def reweight_cut(a_ctau):
            reweights = rate.weight_by_z(chi2.ep.z, chi2.p.energy/chi2.p.mass * a_ctau)
            return ak.sum(reweights), ak.sum(reweights[vtx.pos.fZ > 10])
        df[['reweightsum', 'reweightsum_pass']] = df.apply(lambda row: reweight_cut(row['ctau']), axis=1, result_type='expand')
        df['prod_rate'] = (df.eps2)*params['ap_prod_rate_per_eps2']  # eps=1 value copied from
        df['mchi'] = params['mchi']
        df['rmap'] = params['rmap']
        df['rdmchi'] = params['rdmchi']
        return {
            'signal': {
                'roacc': to_accumulator(df),
                (params['mchi'], params['rdmchi'], params['rmap']): h
            }
        }

    return {
        'bkgd': {
            params['name']: h
        }
    }


def groupby_signal_params(out):
    """unpack, merge, and recalculate the readout-acceptance table in the signal category"""
    out['signal']['roacc_unmerged'] = from_accumulator(out['signal']['roacc'])
    df = out['signal']['roacc_unmerged'].groupby(
        ['eps2', 'mchi', 'rdmchi', 'rmap']
    ).agg(
        {
            'num_pass': np.sum,
            'num_thrown': np.sum,
            'reweightsum': np.sum,
            'reweightsum_pass': np.sum,
            'prod_rate': np.mean
        }
    ).reset_index()
    df['z_cut_eff'] = df.reweightsum_pass / df.reweightsum
    df['event_selection_eff'] = df.num_pass / df.num_thrown
    df['full_eff'] = df.z_cut_eff * df.event_selection_eff
    df['full_rate'] = df.full_eff*df.prod_rate
    out['signal']['roacc'] = df
