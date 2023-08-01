"""reco analyzer"""
import os
import pickle
import json
from pathlib import Path
from typing import Optional

import numpy as np
import awkward as ak
from coffea.nanoevents import NanoEventsFactory, BaseSchema
from coffea.analysis_tools import Weights
from coffea.analysis_tools import PackedSelection
from coffea.processor import accumulate
import hist
from hist.axis import Regular
from coffea import processor

from idmload import VertexReformatter

def recursive_repr(d):
    if isinstance(d, dict):
        return {
            recursive_repr(k): recursive_repr(v)
            for k,v in d.items()
        }
    elif isinstance(d, (int,float,str)):
        return d
    return repr(d)    


def cutflow(selection: PackedSelection, initial_name = 'no_cuts'):
    """generate a cutflow histogram from the passed PackedSelection"""
    h = hist.Hist(
        hist.axis.StrCategory(
            [initial_name]+selection.names,
            name = 'cut'
        )
    )
    for i, cut in enumerate(h.axes[0]):
        # this doesn't allow the variances to be calculated
        # the easiest way around this would be to use the fill
        # method in someway
        h[cut] = ak.sum(selection.require(**{
            c : True
            for j, c in enumerate(selection.names)
            if j < i
        }))
    return h


def safe_divide(numerator: np.array, denominator: np.array, *, fill_value = np.nan):
    if isinstance(denominator, ak.Array):
        denominator = denominator.to_numpy()
    if isinstance(numerator, ak.Array):
        numerator = numerator.to_numpy()
    result = np.full(len(denominator), fill_value, dtype = denominator.dtype)
    result[denominator > 0] = numerator[denominator > 0] / denominator[denominator > 0]
    return result

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

        cal_time_offset = 43.0 if events.metadata['isMC'] else 56.0
        
        vtx_selection = PackedSelection()
        vtx_selection.add('ele_trk_time', vertex.electron.track.time < 10)
        vtx_selection.add('pos_trk_time', vertex.positron.track.time < 10)
        vtx_selection.add('ele_trk_clu_match', vertex.electron.goodness_pid < 10)
        vtx_selection.add('pos_trk_clu_match', vertex.positron.goodness_pid < 10)
        vtx_selection.add('ele_trk_clu_tdiff',
            abs(vertex.electron.track.time - (vertex.electron.cluster.time - cal_time_offset)) < 4
        )
        vtx_selection.add('pos_trk_clu_tdiff',
            abs(vertex.positron.track.time - (vertex.positron.cluster.time - cal_time_offset)) < 4
        )
        vtx_selection.add('ele_pos_clu_tdiff',
            abs(vertex.electron.cluster.time - vertex.positron.cluster.time) < 1.45
        )
        vtx_selection.add('ele_trk_chi2_ndf', 
            safe_divide(vertex.electron.track.chi2, vertex.electron.track.ndf, fill_value = 9000) < 6
        )
        vtx_selection.add('pos_trk_chi2_ndf',
            safe_divide(vertex.positron.track.chi2, vertex.positron.track.ndf, fill_value = 9000) < 6
        )
        vtx_selection.add('ele_n_shared', vertex.electron.track.nShared < 4)
        vtx_selection.add('pos_n_shared', vertex.positron.track.nShared < 4)

        # fill histograms for sensitivity analysis
        histograms['vtxz'].fill(vertex[vtx_selection.all()].pos.fZ)
        histograms['event_cutflow'] = cutflow(event_selection, initial_name = 'all_events')
        histograms['vtx_cutflow'] = cutflow(vtx_selection, initial_name = 'all_vertices')

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
