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

class iDM_Reco(processor.ProcessorABC):
    def __init__(self):
        pass

    def process(self, events):
        """Process a chunk of reconstructed events
        """

        sample = 'signal'
        histograms = {
            name : hist.Hist(ax)
            for name, ax in [
              ('nvtxs', Regular(4,0,4,name = 'nvtxs', label='N Vertices')),
              ('vtxz', Regular(40,-5,195,name = 'vtxz', label='Vertex Z [mm]'))
            ]
        }

        plist = os.path.basename(events.metadata['filename'])[:-5].split('_')
        params = {plist[i]:plist[i+1] for i in range(0,len(plist),2)}

        mchi = int(params['mchi'])
        ratios = str(events.metadata['dataset'])
        
        event_selection = PackedSelection()
        event_selection.add(
            'pair1trigger', 
            events.metadata['isMC']|(events['EventHeader/pair1_trigger_']==1)
        )

        nvtxs = ak.count(
            events['UnconstrainedV0Vertices_KF/UnconstrainedV0Vertices_KF.fUniqueID'],
            axis=1
        )
        print(mchi, ratios, nvtxs)
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

        return {
            ratios : {
              mchi : histograms
            }
        }

    def postprocess(self, accumulator):
        pass


if __name__ == '__main__':
    output_name = 'test.pkl'
    ncores = 1
    quiet = True
    test = True

    base_directory = Path('/export/scratch/users/eichl008/hps/idm/reach/2016/')
    dataset = {
        'rmap-3.00-rdmchi-0.60': {
          'files': [
            str(f)
            for f in (base_directory / 'rmap-3.00-rdmchi-0.60' / 'recon' / 'HPS-PhysicsRun2016-Pass2').iterdir()
            if f.suffix == '.root'
          ], 
          'metadata': {'isMC': True}
        },
    }


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

    print(json.dumps(out, indent=2))

    with open(output_name, 'wb') as outf:
        pickle.dump(out, outf)
