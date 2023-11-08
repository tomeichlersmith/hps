from hpsmc.generators import MG5
from hpsmc.tools import SLIC, JobManager, FilterBunches, BeamCoords, Unzip, DisplaceUni

job.description = 'iDM generation to recon with tuples'

## Generate tritrig in MG5
mg = MG5(name='idm',
         run_card='run_card.dat',
         param_card='param_card.dat',
         event_types=['unweighted'])

## Unzip LHE file
unzip = Unzip(inputs=['idm_unweighted_events.lhe.gz'], outputs=['idm.lhe'])

## Convert LHE output to stdhep (no displacement here because no ctau given)
cnv = DisplaceUni(inputs=['idm.lhe'], outputs=['idm.stdhep'])

## Rotate into beam coords
rot = BeamCoords()

## Run events in slic
slic = SLIC()

## tuplize sim data
mc_tuplize = HPSTR(cfg='mc_tuplize', is_data=0, year=2016)

## Insert empty bunches expected by pile-up simulation
filter_bunches = FilterBunches()

## Run simulated events in readout to generate triggers
readout = JobManager(steering='readout')

## Run physics reconstruction
recon = JobManager(steering='recon')

## tuplize reco data
rec_tuplize = HPSTR(cfg='rec_tuplize', is_data=0, year=2016)

## Run the job
job.add([mg, unzip, cnv, rot, slic, mc_tuplize, filter_bunches, readout, recon, rec_tuplize])
