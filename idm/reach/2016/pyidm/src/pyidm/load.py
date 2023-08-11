"""load iDM (or iDM-related) events into awkward"""

from dataclasses import dataclass, field
from collections.abc import Callable

import awkward as ak

import vector
vector.register_awkward()


def _three_vector(branch_fn, pre_coord, post_coord = ''):
    return ak.zip({
        c: branch_fn(f'{pre_coord}{c}{post_coord}')
        for c in ['x', 'y', 'z']
    }, with_name='Vector3D')


def track(events, coll = 'KalmanFullTracks'):
    def _branch(name):
        return events[f'{coll}.{name}_']
    trk_dict = {
        m: _branch(m)
        for m in [
            'n_hits', 'track_volume', 'type', 'd0', 'phi0',
            'omega', 'tan_lambda', 'z0', 'chi2', 'ndf',
            'id', 'charge', 'nShared', 'SharedLy0', 'SharedLy1'
        ]
    }
    # trk_dict.update({
    #    m : branch(f'{name}_.track_.{m}_[14]')
    #    for m in ['isolation','lambda_kinks','phi_kinks']
    # })
    trk_dict.update({
        'time': _branch('track_time'),
        'p': _three_vector(_branch, 'p', ''),
        'pos_at_ecal': _three_vector(_branch, '', '_at_ecal')
    })
    return ak.zip(trk_dict, with_name='Track')


def cluster(events, coll = 'RecoEcalClusters'):
    def _branch(name):
        return events[f'{coll}.{name}_']
    return ak.zip({
        m : _branch(m)
        for m in ['seed_hit', 'x', 'y', 'z', 'energy', 'time']
    }, with_name='Cluster')


def reco_particle(events, coll = 'FinalStateParticles'):
    def _branch(name):
        return events[f'{coll}.{name}_']
    the_dict = {
        m: _branch(m)
        for m in ['charge', 'type', 'pdg', 'goodness_pid', 'energy', 'mass']
    }
    the_dict.update({
        'p': _three_vector(_branch, 'p'),
        'p_corr': _three_vector(_branch, 'p', '_corr'),
        'track': track(events, coll=f'{coll}.track_'),
        'cluster': cluster(events, coll=f'{coll}.cluster_')
    })
    return ak.zip(the_dict, with_name='Particle')


def vertex(events, coll = 'UnconstrainedV0Vertices_KF'):
    def _branch(name):
        return events[f'{coll}.{name}_']
    the_dict = {
        m: _branch(m)
        for m in [
            'chi2', 'ndf', 'pos', 'p1', 'p2', 'p', 'invM', 'invMerr',
            # 'covariance', leave out for now since it messes up form
            'probability', 'id', 'type'
        ]
    }
    the_dict.update({
        name: reco_particle(events, coll=f'{coll}.{name}_')
        for name in ['electron', 'positron']
    })
    return ak.zip(the_dict, with_name = 'Vertex')


def mc_particles(events, coll='MCParticle'):
    def _branch(name):
        return events[f'{coll}.{name}']

    the_dict = {
        m: _branch(f'{m}_')
        for m in [
            'id', 'charge', 'pdg', 'momPDG', 'gen',
            'sim', 'mass'
        ]
    }
    the_dict.update({
        'p': ak.zip({
            'px': _branch('px_'),
            'py': _branch('py_'),
            'pz': _branch('pz_'),
            'energy': _branch('energy_'),
        }, with_name='Momentum4D'),
        'p_ep': ak.zip({
            'px': _branch('px_ep'),
            'py': _branch('py_ep'),
            'pz': _branch('pz_ep'),
        }, with_name='Momentum3D'),
        'vtx': ak.zip({
            'time': _branch('time_'),
            'x': _branch('vtx_x_'),
            'y': _branch('vtx_y_'),
            'z': _branch('vtx_z_')
        }, with_name='Vector4D'),
        'ep': ak.zip({
            'x': _branch('ep_x_'),
            'y': _branch('ep_y_'),
            'z': _branch('ep_z_'),
        }, with_name='Vector3D')
    })
    return ak.zip(the_dict, with_name='MCParticle')


def mc_tracker_hits(events, coll='TrackerHits'):
    def _branch(name):
        return events[f'{coll}.{name}_']
    the_dict = {
        m: _branch(m)
        for m in ['layer', 'module', 'edep', 'pdg']
    }
    the_dict.update({
        'pos': ak.zip({
            c: _branch(c)
            for c in ['x', 'y', 'z', 'time']
        }, with_name='Vector4D')
    })
    return ak.zip(the_dict, with_name='TrackerHit')


def mc_ecal_hits(events, coll='EcalHits'):
    return ak.zip({
        m: events[f'{coll}.{m}_']
        for m in ['x', 'y', 'z', 'system', 'ix', 'iy', 'energy']
    }, with_name='EcalHit')


def identity_reformat(a):
    return a


def recursplit(the_dict, fieldname, array):
    """Recursively split a field by '.' into subfields
    inserting new dicts along the way eventually inserting
    the array itself

    Parameters
    ----------
    the_dict: dict
        dictionary we will be reading and writing
    fieldname: str
        fieldname to split
    array: ak.Array
        array that field is naming
    """
    subfields = fieldname.split('.', maxsplit=1)
    if len(subfields) == 1:
        if subfields[0] in the_dict:
            raise Exception('Two fields deduced to the same tree location.')
        the_dict[subfields[0]] = array
    else:
        if subfields[0] not in the_dict:
            the_dict[subfields[0]] = {}
        recursplit(the_dict[subfields[0]], subfields[1], array)


def hps_mc_reformat(events):
    hps_dict = {
        name : events[name] 
        for name in events.fields 
        if '.' not in name 
    }
    hps_dict['mc_particle'] = mc_particles(events)
    hps_dict['mc_tracker_hits'] = mc_tracker_hits(events)
    hps_dict['mc_ecal_hits'] = mc_ecal_hits(events)
    return ak.zip(hps_dict, depth_limit=1)


def hps_reco_reformat(events):
    hps_dict = {
        name : events[name] 
        for name in events.fields 
        if '.' not in name 
    }
    hps_dict['vertex'] = vertex(events)
    hps_dict['track'] = track(events)
    hps_dict['cluster'] = cluster(events)
    hps_dict['mc_particle'] = mc_particles(events)
    return ak.zip(hps_dict, depth_limit=1)


@dataclass
class FromROOT:
    treename: str
    open_kw: dict = field(default_factory=dict)
    arrays_kw: dict = field(default_factory=dict)
    reformatter: Callable = field(default=identity_reformat)

    def __call__(self, fp):
        import uproot
        with uproot.open(fp, **self.open_kw) as f:
            events = f[self.treename].arrays(**self.arrays_kw)
        return self.reformatter(events)


    @staticmethod
    def hps_mc(**kwargs):
        if 'reformatter' not in kwargs:
            kwargs['reformatter'] = hps_mc_reformat
        return FromROOT('HPS_Event', **kwargs)


    @staticmethod
    def hps_reco(**kwargs):
        if 'reformatter' not in kwargs:
            kwargs['reformatter'] = hps_reco_reformat
        return FromROOT('HPS_Event', **kwargs)
