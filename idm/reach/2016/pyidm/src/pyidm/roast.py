"""load iDM (or iDM-related) events into awkward"""

import awkward as ak
from coffea.nanoevents import NanoEventsFactory, BaseSchema

import vector
vector.register_awkward()


class VertexReformatter:
    """This class restructures the in-memory awkward event array into
    a better-structture awkward array with some vector behaviors attached
    """

    def __init__(self, events, vertex_coll='UnconstrainedV0Vertices_KF'):
        self.vertex_coll = vertex_coll
        self.events = events

    def _branch(self, name):
        return ak.flatten(self.events[f'{self.vertex_coll}/{self.vertex_coll}.{name}'])

    def _three_vector(self, pre_coord, post_coord):
        return ak.zip({
            c: self._branch(f'{pre_coord}{c}{post_coord}')
            for c in ['x', 'y', 'z']
        }, with_name='Vector3D')

    def track(self, name):
        trk_dict = {
            m: self._branch(f'{name}_.track_.{m}_')
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
            'time': self._branch(f'{name}_.track_.track_time_'),
            'p': self._three_vector(f'{name}_.track_.p', '_'),
            'pos_at_ecal': self._three_vector(f'{name}_.track_.', '_at_ecal_')
        })
        return ak.zip(trk_dict, with_name='Track')

    def cluster(self, name):
        clu_dict = {
            m: self._branch(f'{name}_.cluster_.{m}_')
            for m in ['seed_hit', 'x', 'y', 'z', 'energy', 'time']
        }
        return ak.zip(clu_dict, with_name='Cluster')

    def particle(self, name):
        the_dict = {
            m: self._branch(f'{name}_.{m}_')
            for m in ['charge', 'type', 'pdg', 'goodness_pid', 'energy', 'mass']
        }
        the_dict.update({
            'p': self._three_vector(f'{name}_.p', '_'),
            'p_corr': self._three_vector(f'{name}_.p', '_corr_'),
            'track': self.track(name),
            'cluster': self.cluster(name)
        })
        return ak.zip(the_dict, with_name='Particle')

    def vertex(self):
        vtx_dict = {
            m: self._branch(f'{m}_')
            for m in [
                'chi2', 'ndf', 'pos', 'p1', 'p2', 'p', 'invM', 'invMerr',
                # 'covariance', leave out for now since it messes up form
                'probability', 'id', 'type']
        }
        vtx_dict.update({
            p: self.particle(p)
            for p in ['electron', 'positron']
        })
        return ak.zip(vtx_dict, with_name='Vertex')

    def __call__(self):
        return self.vertex()


def from_root(fp, **kwargs):
    """Mimic the load mechanism of coffea so we can test VertexReformatter
    and inspect the resulting events in a jupyter notebook
    """
    return NanoEventsFactory.from_root(
        fp, 'HPS_Event',
        schemaclass=BaseSchema,
        **kwargs
    ).events()


def vertices(fp, vertex_coll='UnconstrainedV0Vertices_KF', **kwargs):
    events = from_root(fp, **kwargs)
    nvtxs = ak.count(events[f'{vertex_coll}/{vertex_coll}.fUniqueID'], axis=1)
    return VertexReformatter(events[nvtxs == 1], vertex_coll=vertex_coll)()
