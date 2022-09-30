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
  -d HPS_Nominal_201920216SensorSurvey_iter0 \
  -D outputFile=data_events_aliRecon \
  alignmentDriver_chi2.lcsim \
  -n 10 \
  -i /sdf/group/hps/data/physrun2019/hps_010031/HPS_PhysicsRun2019-v2-FEE-Pass0/data_events_141.slcio
```
