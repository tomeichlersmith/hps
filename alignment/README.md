# Alignment with Kalman Tracks

The steering file in this directory is mean to re-run the kalman
tracking on an existing LCIO file and output the data files necessary
for `pede` to find a new set of alignment parameters.

```
java \
  -DdisableSvtAlignmentConstants \
  -Djna.library.path=/sdf/group/hps/users/pbutti/sw/GeneralBrokenLines/cpp/install/lib/ \
  -XX:+UseSerialGC \
  -Xmx5000m \
  -jar /sdf/group/hps/users/eichl008/hps/java/distribution/target/hps-distribution-5.1-SNAPSHOT-bin.jar \
  -R 10031 \
  -d HPS_Nominal_2019SensorSurvey_iter0 \
  -D outputFile=data_events_aliRecon \
  alignmentDriver_chi2.lcsim \
  -n 10 \
  -i /sdf/group/hps/data/physrun2019/hps_010031/HPS_PhysicsRun2019-v2-FEE-Pass0/data_events_141.slcio
```

### Detectors `-d`
These are listed in `<hps-java>/detector-data/detectors/` and should match the year of the data.

### Run `-R`
This is where the run number is defined in the data files (I believe) and it should match the
run number of the data that was taken and is being processed.

### Output Files
`<outname>_kfgblplots.root` has histograms related to the tracking infrastructre and its results.

`<outname>_all_millepede_kf_PC.bin` is the prepared data file for millepede

### MC
```
/sdf/group/hps/mc/
  - tritrig/slic/<beam>/<run>
```
...need to find some more that can be helpful
a good start
```
/sdf/group/hps/mc/4pt55GeV/fee/idealCond/fee_recon_20um120nA_*
```

## What do
Unless otherwise noted, the commands are run in this directory and the
container environment has already been initialized and configured.

Copy down a single partition of the provided ideal FEE MC sample.
```
scp slac.sdf:/sdf/group/hps/mc/4pt55GeV/fee/idealCond/fee_recon_20um120nA_200.slcio .
```
Going to use run number 10716 for this right now since those conditions are taken
from a pretty good real FEE run in 2019.

Go to `hps-java`, create a new copy of `HPS_Nominal_2019SensorSurvey_iter0` (I just called it the same, incrementing the iter number), manually modify the `millepede_constant`s, and construct the `lcdd` file.
```
# in hps-java root directory
hps bash ../alignment/construct_detector.sh iter1 Nominal_2019SensorSurvey
```
- Using `JeffersonLab:jna_composed_traj` branch
- Until a java configuration issue is resolved, we need to mount the home directory
  and symlink `~/.cache/lcsim` to `${HPS_CONTAINER_INSTALL}/.cache/lcsim` so caching
  is still functional.

Run tracking over both iterations of the detector and for both KF and GBL tracks.
```
hps bash run.sh
```

Check the `*log` files to make sure the four runs completed successfully.

Open up the output `*root` files in the notebook for study.
