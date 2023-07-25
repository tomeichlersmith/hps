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
        
        selection = PackedSelection()
        selection.add(
            'pair1trigger', 
            events['EventHeader/pair1_trigger_']==1
        )

        nvtxs = ak.count(
            events['UnconstrainedV0Vertices_KF/UnconstrainedV0Vertices_KF.fUniqueID'],
            axis=1
        )
        histograms['nvtxs'] = hist.Hist(Regular(4,0,4,label='N Vertices'))
        histograms['nvtxs'].fill(nvtxs)
        
        selection.add(
            'singlevtx',
            nvtxs==1
        )

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
        'rmap-3.00-rdmchi-0.60': ['test.root'],
    }

    # TODO: status is not affecting whether the progress bars are being drawn
    runner = processor.Runner(
        executor = processor.FuturesExecutor(
            workers = ncores, 
            compression = None, 
            status = not quiet
        ),
        schema = BaseSchema,
    )

    p = iDM_Reco()

    out = runner(
        dataset,
        treename = 'HPS_Event',
        processor_instance = p
    )

    for sample, data in out.items():
        print(sample, {k:v for k,v in data.items() if k != 'histograms'})

    with open(output_name, 'wb') as outf:
        pickle.dump(out, outf)
