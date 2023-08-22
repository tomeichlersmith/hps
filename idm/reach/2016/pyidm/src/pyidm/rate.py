"""Calculate dark photon production and chi2 decay rate"""

import pandas as pd
import numpy as np
import awkward as ak
import uproot

lumi = 10.7  # pb^{-1}
inverse_alpha = 137


def radFrac(mass):
    """total radiative fraction polynomial fit to MC distributions

    calculated by Alic Spellman for 2016 SIMPs using KF tracking on 11/15/22
    """
    radF = -1.04206e-01 \
        + 9.92547e-03*mass \
        + -1.99437e-04*pow(mass, 2) \
        + 1.83534e-06*pow(mass, 3) \
        + -7.93138e-9*pow(mass, 4) \
        + 1.30456e-11*pow(mass, 5)
    return radF


def totRadAcc(mass):
    """Total radiative acceptance polynomial fit to MC distributions

    calculated by Alic Spellman for 2016 SIMPs using KF tracking on 11/15/22
    """
    acc = -7.35934e-01 \
        + 9.75402e-02*mass \
        - 5.22599e-03*pow(mass, 2) \
        + 1.47226e-04*pow(mass, 3) \
        - 2.41435e-06*pow(mass, 4) \
        + 2.45015e-08*pow(mass, 5) \
        - 1.56938e-10*pow(mass, 6) \
        + 6.19494e-13*pow(mass, 7) \
        - 1.37780e-15*pow(mass, 8) \
        + 1.32155e-18*pow(mass, 9)
    return acc


def dNdm(mass, binwidth=30.0):
    value = 0.0
    for name, pack in dNdm.__raw_data.items():
        t = pack['tree']
        value += ak.sum(
            (t['unc_vtx_mass']*1000 > mass - binwidth/2) & (t['unc_vtx_mass']*1000 < mass + binwidth/2)
        )*pack['scale']
    return value/binwidth


dNdm.__raw_data = {
    'tritrig': {
        'file': '../../simp-rate/final_hadd_tritrigv2-beamv6_2500kBunches_HPS-PhysicsRun2016-Pass2_v4_5_0_pairs1_976_KF_CR.root',
        'scale': 1.416e9*lumi/(50000*9853)
    },
    'wab': {
        'file': '../../simp-rate/final_hadd_wabv3-beamv6_2500kBunches_HPS-PhysicsRun2016-Pass2_v4_5_0_pairs1_KF_ana_CR.root',
        'scale': 0.1985e12*lumi/(100000*9966)
    }
}

for name, pack in dNdm.__raw_data.items():
    with uproot.open(pack['file']) as f:
        pack['tree'] = f['vtxana_kf_vertexSelection_Tight_CR/vtxana_kf_vertexSelection_Tight_CR_tree'].arrays()


def darkphoton_production(mass):
    if totRadAcc(mass) > 0:
        return (3*inverse_alpha/2)*np.pi*mass*radFrac(mass)*dNdm(mass)/totRadAcc(mass)
    else:
        return 0


def rate(mchi, rdmchi, rmap):
    opts = rate.__lut__[
        (rate.__lut__['mchi'] == mchi)
        & (rate.__lut__['rdmchi'] == rdmchi)
        & (rate.__lut__['rmap'] == rmap)
    ]
    if len(opts) == 0:
        raise ValueError(f'No width calculated for {(mchi, rdmchi, rmap)}.')
    return opts.chi2_width_per_epsilon.mean()


rate.__lut__ = pd.concat([pd.read_csv('umn-signal-width.csv'), pd.read_csv('umn-signal-dense-width.csv')])


def ctau(rate):
    c = 3.00e10  # cm/s
    hbar = 6.58e-25  # GeV*sec
    return c*hbar/rate


def weight_by_z(z, gamma_c_tau):
    return np.exp((-4.3 - z)/gamma_c_tau)/gamma_c_tau
