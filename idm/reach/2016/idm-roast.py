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


def recursive_repr(d):
    if isinstance(d, dict):
        return {
            recursive_repr(k): recursive_repr(v)
            for k,v in d.items()
        }
    elif isinstance(d, (int,float,str)):
        return d
    return repr(d)    


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
        
        ele_trk_time = events['UnconstrainedV0Vertices_KF/UnconstrainedV0Vertices_KF.electron_.track_.track_time_']
        pos_trk_time = events['UnconstrainedV0Vertices_KF/UnconstrainedV0Vertices_KF.positron_.track_.track_time_']
        
        vtx_selection = PackedSelection()
        vtx_selection.add(
            'ele_trk_time',
            ak.flatten(ele_trk_time[event_selection.all()] < 10)
        )
        vtx_selection.add(
            'pos_trk_time',
            ak.flatten(pos_trk_time[event_selection.all()] < 10)
        )

        vtxz = ak.flatten(
            events['UnconstrainedV0Vertices_KF/UnconstrainedV0Vertices_KF.pos_'] \
                .fZ[event_selection.all()]
        )[vtx_selection.all()]

        # fill histograms for sensitivity analysis
        histograms['vtxz'].fill(vtxz)

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
        base_directory = Path('/sdf/group/hps/users/eichl008/hps/idm/reach/2016/')
        dataset = {
            'rmap-3.00-rdmchi-0.60-mchi-030': {
              'files': [
                str(f)
                for f in (
                  base_directory / 'rmap-3.00-rdmchi-0.60-mchi-030' / 'output' / 
                  'recon' / 'HPS-PhysicsRun2016-Pass2'
                ).iterdir()
                if f.suffix == '.root'
              ], 
              'metadata': {'isMC': True}
            },
            'tritrig': {
              'files': [
                str(f)
                for f in (base_directory / 'bkgd' / 'tritrig' / 'tuples').iterdir()
                if f.suffix == '.root'
              ],
              'metadata': {'isMC': True}
            },
            'wab': {
              'files': [
                str(f)
                for f in (base_directory / 'bkgd' / 'wab' / 'tuples').iterdir()
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
