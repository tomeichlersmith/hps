"""reco analyzer"""
import os
import pickle
import json
from pathlib import Path
from typing import Optional

import awkward as ak
from coffea.nanoevents import NanoEventsFactory, BaseSchema
from coffea.analysis_tools import Weights
from coffea.analysis_tools import PackedSelection
from coffea.processor import accumulate
import hist
from hist.axis import Regular
from coffea import processor

import vector
vector.register_awkward()

def recursive_repr(d):
    if isinstance(d, dict):
        return {
            recursive_repr(k): recursive_repr(v)
            for k,v in d.items()
        }
    elif isinstance(d, (int,float,str)):
        return d
    return repr(d)    


class VertexReformatter:
    def __init__(self, events, vertex_coll = 'UnconstrainedV0Vertices_KF'):
        self.vertex_coll = vertex_coll
        self.events = events
    
    def _branch(self, name):
        return ak.flatten(self.events[f'{self.vertex_coll}/{self.vertex_coll}.{name}'])
    
    def _three_vector(self, pre_coord, post_coord):
        return ak.zip({
            c : self._branch(f'{pre_coord}{c}{post_coord}')
            for c in ['x','y','z']
        }, with_name = 'Vector3D')
  
    def track(self, name):
        trk_dict = {
            m : self._branch(f'{name}_.track_.{m}_')
            for m in [
                'n_hits','track_volume','type','d0','phi0',
                'omega','tan_lambda','z0','chi2','ndf','track_time',
                'id','charge','nShared','SharedLy0','SharedLy1'
            ]
        }
        #trk_dict.update({
        #    m : branch(f'{name}_.track_.{m}_[14]')
        #    for m in ['isolation','lambda_kinks','phi_kinks']
        #})
        trk_dict.update({
            'p' : self._three_vector(f'{name}_.track_.p','_'),
            'pos_at_ecal': self._three_vector(f'{name}_.track_.','_at_ecal_')
        })
        return ak.zip(trk_dict, with_name = 'Track')
    
    def cluster(self, name):
        clu_dict = {
            m : self._branch(f'{name}_.cluster_.{m}_')
            for m in ['seed_hit','x','y','z','energy','time']
        }
        return ak.zip(clu_dict, with_name = 'Cluster')
    
    def particle(self, name):
        the_dict = {
            m : self._branch(f'{name}_.{m}_')
            for m in ['charge','type','pdg','goodness_pid','energy','mass']
        }
        the_dict.update({
            'p' : self._three_vector(f'{name}_.p','_'),
            'p_corr' : self._three_vector(f'{name}_.p','_corr_'),
            'track': self.track(name),
            'cluster': self.cluster(name)
        })
        return ak.zip(the_dict, with_name = 'Particle')
    
    def vertex(self):
        vtx_dict = {
            m : self._branch(f'{m}_')
            for m in [
                'chi2','ndf','pos','p1','p2','p','invM','invMerr',
                #'covariance', leave out for now since it messes up form
                'probability','id','type']
        }
        vtx_dict.update({
            p : self.particle(p)
            for p in ['electron','positron']
        })
        return ak.zip(vtx_dict, with_name='Vertex')

    def __call__(self):
        return self.vertex()

class iDM_Reco(processor.ProcessorABC):
    def __init__(self):
        pass

    def process(self, events):
        """Process a chunk of reconstructed events
        """

        histograms = {
            name : hist.Hist(ax)
            for name, ax in [
              ('nvtxs', Regular(4,0,4,name = 'nvtxs', label='N Vertices')),
              ('vtxz', Regular(40,-5,195,name = 'vtxz', label='Vertex Z [mm]'))
            ]
        }
        
        event_selection = PackedSelection()
        event_selection.add(
            'pair1trigger', 
            events.metadata['isMC']|(events['EventHeader/pair1_trigger_']==1)
        )

        nvtxs = ak.count(
            events['UnconstrainedV0Vertices_KF/UnconstrainedV0Vertices_KF.fUniqueID'],
            axis=1
        )
        histograms['nvtxs'].fill(nvtxs)
        
        event_selection.add(
            'singlevtx',
            nvtxs==1
        )

        vertex = VertexReformatter(events[event_selection.all()])()
        
        vtx_selection = PackedSelection()
        vtx_selection.add(
            'ele_trk_time',
            vertex.electron.track.track_time < 10
        )
        vtx_selection.add(
            'pos_trk_time',
            vertex.positron.track.track_time < 10
        )

        # fill histograms for sensitivity analysis
        histograms['vtxz'].fill(vertex[vtx_selection.all()].pos.fZ)

        # convert '_'-separated parameters in filename into a dictionary
        #   assumes filename is <key0>_<val0>_<key1>_<val1>_...<keyN>_<valN>.root
        #plist = os.path.basename(events.metadata['filename'])[:-5].split('_')
        #params = {plist[i]:plist[i+1] for i in range(0,len(plist),2)}

        return { events.metadata['dataset'] : histograms }

    def postprocess(self, accumulator):
        pass

    def run(
        output_name : Path, 
        ncores: Optional[int] = 1, 
        quiet: Optional[bool] = True, 
        test: Optional[bool] = False
    ):
        #base_directory = Path('/sdf/group/hps/users/eichl008/hps/idm/reach/2016/')
        base_directory = Path('/local/cms/user/eichl008/hps/idm')
        dataset = {
            'rmap-3.00-rdmchi-0.60-mchi-030': {
              'files': [
                str(base_directory / 'signal' / 'idm_2pt3_mchi_030_rmap_3.00_rdmchi_0.60_nruns_200_nevents_10k.root')
              ], 
              'metadata': {'isMC': True}
            },
            'tritrig': {
              'files': [
                str(f)
                for f in (base_directory / 'bkgd' / 'tritrig').iterdir()
                if f.suffix == '.root'
              ],
              'metadata': {'isMC': True}
            },
            'wab': {
              'files': [
                str(f)
                for f in (base_directory / 'bkgd' / 'wab').iterdir()
                if f.suffix == '.root'
              ],
              'metadata': {'isMC': True}
            }
        }
    
        if test:
            for entry in dataset:
                dataset[entry]['files'] = dataset[entry]['files'][:2]
        else:
            # BAD - need to figure out how to get coffea to ignore branches
            import warnings
            warnings.filterwarnings('ignore')
    
        p = iDM_Reco()
    
        executor = (
            processor.IterativeExecutor() if test else 
            processor.FuturesExecutor(workers = ncores, compression = None)
        )
    
        runner = processor.Runner(
            executor = executor,
            schema = BaseSchema,
        )
    
        out = runner(
            dataset,
            treename = 'HPS_Event',
            processor_instance = p,
        )
    
        with open(output_name, 'wb') as outf:
            pickle.dump(out, outf)
    
        print(json.dumps(recursive_repr(out), indent=2))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('output_name', type=Path, help='output pickle file to save histograms to')
    parser.add_argument('--n-cores', '-j', type=int, help='number of cores to use during processing', default=4)
    parser.add_argument('--test', action='store_true', help='just a test run, decrease number of files')

    args = parser.parse_args()

    iDM_Reco.run(args.output_name, args.n_cores, True, args.test)
