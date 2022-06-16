import HpstrConf
import sys
import os
import baseConfig

options = baseConfig.parser.parse_args()

p = HpstrConf.Process()

p.run_mode = 1
#p.max_events = 1000

p.input_files = options.inFilename
p.output_files = [ p.input_files[0].replace('tuple','hist') ]

# Library containing processors
p.add_library("libprocessors")

beamE = 2.3 # GeV - 2016 data

###############################
#          Processors         #
###############################

ana = HpstrConf.Processor('ana', 'ThreeProngTridentTracksAnalyzer')
ana.parameters["debug"] = 1

hpstr_analysis_dir=f'{os.environ["HPSTR_BASE"]}/analysis'
selections_dir = f'{hpstr_analysis_dir}/selections/three-prong-tridents'

ana.parameters["cluster_selection"] = f'{selections_dir}/three-prong-trident-cluster-selection.json'
ana.parameters["event_selection"] = f'{selections_dir}/three-prong-trident-event-selection.json'
ana.parameters["histo_cfg"] = f'{hpstr_analysis_dir}/plotconfigs/three-prong-tridents/three-prong-trident-histos-{beamE}GeV.json'
ana.parameters["beamE"] = beamE
ana.parameters["isData"] = options.isData

CalTimeOffset=-999.
if (options.isData==1):
    CalTimeOffset=56.
    print("Running on data file: Setting CalTimeOffset %d"  % CalTimeOffset)
elif (options.isData==0):
    CalTimeOffset=43.
    print("Running on MC file: Setting CalTimeOffset %d"  % CalTimeOffset)
else:
    print("Specify which type of ntuple you are running on: -t 1 [for Data] / -t 0 [for MC]")

ana.parameters["CalTimeOffset"]=CalTimeOffset

p.sequence = [ana]

p.printProcess()

