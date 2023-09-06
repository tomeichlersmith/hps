from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import numpy as np
import awkward as ak
import hist
import uproot

from . import rate
from .mfsa.accumulator import to_accumulator, from_accumulator


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

    if 'idm' not in params:
        raise ValueError('Only analyzing signal samples right now!')
    
    h = SimpleNamespace()

    n_vtx = ak.count(events.vertex.chi2, axis=1)
    h.n_vtx = hist.Hist(
        hist.axis.IntCategory(
            [0,1,2,3],
            label='N Vertices in Event'
        )
    )
    h.n_vtx.fill(n_vtx)
    
    event_selections = {
        'multi_vertex' : n_vtx>1,
        'one_vertex': n_vtx==1,
        'no_vertex' : n_vtx==0
    }

    vtx = ak.flatten(events[event_selections['one_vertex']].vertex)

    h.vtx = hist.Hist(
        hist.axis.Regular(
            130, -80, 180,
            name='vtxz',
            label='Vertex Z [mm]'
        )
    )
    h.vtx.fill(vtx.pos.fZ)

    h.n_trks = hist.Hist(
        hist.axis.StrCategory(
            list(event_selections.keys()),
            name='sl',
        ),
        hist.axis.Regular(
            5, 0, 5,
            name='n_ele_trks',
            label='Num Reco Electron Tracks'
        ),
        hist.axis.Regular(
            5, 0, 5,
            name='n_pos_trks',
            label='Num Reco Positron Tracks'
        ),
        hist.axis.Regular(
            3,-1.5,1.5,
            name='opp_pair_exists',
            label='$e^+e^-$ Pair of Tracks in Oppositive Halves Exists'
        )
    )
    for slname, sl in event_selections.items():
        electrons = events[sl].track[events[sl].track.charge < 0]
        positrons = events[sl].track[events[sl].track.charge > 0]
        epem_pairs = ak.cartesian({'electron':electrons,'positron':positrons})
        pair_exists = (
            ak.fill_none(
                ak.max(
                    np.sign(
                        epem_pairs.electron.tan_lambda*epem_pairs.positron.tan_lambda
                    )*-1,
                    axis=1
                ),
                -3
            )+1)/2
        h.n_trks.fill(
            sl=slname,
            n_ele_trks=ak.count(electrons.id, axis=1),
            n_pos_trks=ak.count(positrons.id, axis=1),
            opp_pair_exists = pair_exists
        )
    

    # readout-level acceptance calculations
    df = pd.DataFrame({'eps2': np.logspace(-2, -6)})
    df['ctau'] = rate.ctau(params['chi2_width_per_eps2']*df.eps2)
    df['num_thrown'] = params['nevents']*params['nruns']
    df['prod_rate'] = (df.eps2)*params['ap_prod_rate_per_eps2']  # eps=1 value copied from
    df['mchi'] = params['mchi']
    df['rmap'] = params['rmap']
    df['rdmchi'] = params['rdmchi']

    # we do the same re-weighting procedure for each analysis selection

    # standard, single-vertex displaced analysis
    #   we require exactly one vertex in the event, make quality cuts on it,
    #   and then count how many events are pass some z cut
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
    
    df['std_num_pass'] = ak.count(vtx[vtx_sel].chi2)

    def std_reweight_cut(a_ctau):
        chi2 = ak.flatten(
            events[event_selections["one_vertex"]].mc_particle[
                events[event_selections["one_vertex"]].mc_particle.pdg == 1000023
            ]
        )[vtx_sel]
        reweights = rate.weight_by_z(chi2.ep.z, chi2.p.energy/chi2.p.mass * a_ctau)
        return ak.sum(reweights), ak.sum(reweights[vtx[vtx_sel].pos.fZ > 10])
    
    df[['std_reweightsum', 'std_reweightsum_pass']] = df.apply(
        lambda row: std_reweight_cut(row['ctau']), 
        axis=1, 
        result_type='expand'
    )

    # modified, single-side displaced vertex analysis
    #   use conversion vertices rather than standard, opposite-side vertices
    # our event selection requires there to be at least one conversion vertex
    #   and an electron track in the opposite half
    #   so we could feasibly deduce which is the "produced" electron at reco time
    n_cvtx = ak.count(events.conv_vertex.chi2, axis=1)
    h.n_cvtx = hist.Hist(
        hist.axis.IntCategory(
            [0,1,2,3],
            label='N Vertices in Event'
        )
    )
    h.n_cvtx.fill(n_cvtx)

    has_cvtx = (
        n_cvtx>0
    )
    
    ele_tracks_in_opp_half = (ak.count(
        events.track[(
            (events.track.charge<0)
            &(
                ak.fill_none(
                    ak.firsts(events.conv_vertex.electron.track.id,axis=1),
                    0
                )!=events.track.id
            )&(
                ak.fill_none(
                    ak.firsts(np.sign(events.conv_vertex.pos.fY),axis=1),
                    0
                )!=np.sign(events.track.tan_lambda)
            )
        )].id,
        axis=1
    )>0)

    mod_selection = has_cvtx&ele_tracks_in_opp_half
    
    h.cvtx = hist.Hist(
        hist.axis.StrCategory(
            ['all','selected']
        ),
        hist.axis.Regular(
            50, -100, 400,
            name='vtxz',
            label='Vertex Z [mm]'
        )
    )
    h.cvtx.fill('all',ak.flatten(events.conv_vertex.pos.fZ,axis=None))
    h.cvtx.fill('selected',ak.flatten(events[mod_selection].conv_vertex.pos.fZ,axis=None))

    df['mod_num_pass'] = ak.sum(mod_selection)

    def mod_reweight_cut(a_ctau):
        chi2 = ak.flatten(
           events[mod_selection].mc_particle[
                events[mod_selection].mc_particle.pdg == 1000023
            ]
        )
        reweights = rate.weight_by_z(chi2.ep.z, chi2.p.energy/chi2.p.mass * a_ctau)
        return ak.sum(
            reweights
        ), ak.sum(
           reweights[ak.flatten(events[mod_selection].conv_vertex.pos.fZ) > 10]
        )
    
    df[['mod_reweightsum', 'mod_reweightsum_pass']] = df.apply(
        lambda row: mod_reweight_cut(row['ctau']), 
        axis=1, 
        result_type='expand'
    )

    return {
        'signal': {
            'roacc': to_accumulator(df),
            (params['mchi'], params['rdmchi'], params['rmap']): vars(h)
        }
    }


def groupby_signal_params(out):
    """unpack, merge, and recalculate the readout-acceptance table in the signal category"""
    df = from_accumulator(out['signal']['roacc']).groupby(
        ['eps2', 'mchi', 'rdmchi', 'rmap']
    ).agg(
        {
            'num_thrown': np.sum,
            'prod_rate': np.mean,
            'std_num_pass': np.sum,
            'std_reweightsum': np.sum,
            'std_reweightsum_pass': np.sum,
            'mod_num_pass': np.sum,
            'mod_reweightsum': np.sum,
            'mod_reweightsum_pass': np.sum,
        }
    ).reset_index()
    for ana in ['std','mod']:
        df[f'{ana}_z_cut_eff'] = df[f'{ana}_reweightsum_pass']/df[f'{ana}_reweightsum']
        df[f'{ana}_event_selection_eff'] = df[f'{ana}_num_pass']/df.num_thrown
        df[f'{ana}_full_eff'] = df[f'{ana}_z_cut_eff']*df[f'{ana}_event_selection_eff']
        df[f'{ana}_full_rate'] = df[f'{ana}_full_eff']*df.prod_rate
    out['signal']['roacc'] = df
