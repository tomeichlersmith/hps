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

        histograms = {}
        
        event_selection = PackedSelection()
        event_selection.add(
            'pair1trigger', 
            events.metadata['isMC']|(events['EventHeader/pair1_trigger_']==1)
        )

        nvtxs = ak.count(
            events['UnconstrainedV0Vertices_KF/UnconstrainedV0Vertices_KF.fUniqueID'],
            axis=1
        )
        histograms['nvtxs'] = hist.Hist(Regular(4,0,4,label='N Vertices'))
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
        histograms['vtxz'] = hist.Hist(Regular(40,-5,195,label='Vtx Z [mm]'))
        histograms['vtxz'].fill(vtxz)

        return {
            events.metadata['dataset'] : {
                'histograms': histograms
            }
        }

    def postprocess(self, accumulator):
        pass


if __name__ == '__main__':
    output_name = 'test.pkl'
    ncores = 1
    quiet = True
    dataset = {
        'rmap-3.00-rdmchi-0.60': {'files': ['test.root'], 'metadata': {'isMC': True}},
    }
    test = True


    p = iDM_Reco()

    executor = (
        processor.IterativeExecutor() if test else 
        processor.FuturesExecutor(workers = ncores, compression = None)
    )

    runner = processor.Runner(
        executor = executor,
        schema = BaseSchema
    )

    out = runner(
        dataset,
        treename = 'HPS_Event',
        processor_instance = p,
    )

    for sample, data in out.items():
        print(sample, {k:v for k,v in data.items() if k != 'histograms'})

    with open(output_name, 'wb') as outf:
        pickle.dump(out, outf)
