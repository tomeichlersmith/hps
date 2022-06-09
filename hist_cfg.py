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

###############################
#          Processors         #
###############################

ana = HpstrConf.Processor('ana', 'FullTridentTracksAnalyzer')
ana.parameters["debug"] = 1

ana.parameters["event_selection"] = os.environ['HPS_HOME']+"/trident-event-selection.json"
ana.parameters["histo_cfg"] = os.environ['HPS_HOME']+"/track_histos-2.3GeV.json"
ana.parameters["beamE"] = 2.3
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

