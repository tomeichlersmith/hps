# 2016 Alignment

Studying how updated Kalman Filter (KF) track finding effects the 2016 alignment.
Can we improve it?

*Table of Contents*
- `pede`: template directory for running pede via hps-mc
- `tracking`: template directory for running batch tracking via hps-mc
  - includes steering file used for hps-java

## Iteration Instructions
1. Make new directory for new detector iteration `mkdir HPS-PhysicsRun2016-KF-iter0`
2. Write detector variables 
```
echo '{"detector" : ["HPS-PhysicsRun2016-KF-iter0"]}' |\
  jq . > HPS-PhysicsRun2016-KF-iter0/tracking-vars.json
```
3. Write tracking jobs
```
hps-mc-job-template \
  -j 1 \
  -a HPS-PhysicsRun2016-KF-iter0/tracking-vars.json \
  -i events tracking/physrun-2016-part-007800-HPS-PhysicsRun2016-Pass2.list 1 \
  tracking/job.json.templ \
  HPS-PhysicsRun2016-KF-iter0/tracking-jobs.json
```
4. Run tracking in batch
```
hps-mc-batch slurm \
  track_align \
  --env $(which hps-mc-env.sh) \
  -S HPS-PhysicsRun2016-KF-iter0/sh \
  -l HPS-PhysicsRun2016-KF-iter0/log \
  -d HPS-PhysicsRun2016-KF-iter0/scratch \
  --memory 3500 \
  -c batch.cfg \
  HPS-PhysicsRun2016-KF-iter0/tracking-jobs.json
```
5. Wait 2-3 hours (about how long it takes for all 367 files to be processed)
6. List full paths of millepede bin files
```
mkdir HPS-PhysicsRun2016-KF-iter0/pede
find $PWD/HPS-PhysicsRun2016-KF-iter0/tracking -type f -name "*.bin" > HPS-PhysicsRun2016-KF-iter0/pede/iter0-mille-bin.list
```
7. Write config for pede step (putting it in `HPS-PhysicsRun2016-KF-iter0/pede/job.json`). Modify the detector name and which parameters you wish to float during the pede optimization.
```json
{
  "output_files": {
    "millepede.res": "millepede.res",
    "millepede.his": "millepede.his",
    "millepede.log": "millepede.log",
    "pede-steer.txt": "pede-steer.txt",
    "merged-gblplots.root": "merged-gblplots.root"
  },
  "force": true,
  "input_files": "HPS-PhysicsRun2016-KF-iter0/pede/iter0-mille-bin.list",
  "output_dir" : "HPS-PhysicsRun2016-KF-iter0/pede",
  "detector"   : "HPS-PhysicsRun2016-KF-iter0",
  "to_float": [
    "individual & tu & layer=3",
    "individual & tu & layer=4",
    "individual & tu & layer=5"
  ]
}
```
8. Run pede step
```
hps-mc-job run \
  -d HPS-PhysicsRun2016-KF-iter0/pede/scratch \
  -c pede/run.cfg \
  pede HPS-PhyscisRun2016-KF-iter0/pede/job.json
```

## Notes

#### General Directory of 2016 Data at SDF
```
/sdf/group/hps/data/physrun2016/
```

### Directory of Reconstructed Data
```
/sdf/group/hps/data/physrun2016/recon/HPS-PhysicsRun2016-Pass2/hps_007800
```
I removed a few partitions from my list of this directory because `dumpevent`
said there were no events in it.
- 28, 358, 20, 76, 29, 26, 25, 80, 24, 204, 385, 30, 209, 19, 203, 99, 27, 206, 205

Found these by
```bash
while read line; do
  if ! dumpevent ${line} 1 &> dumpevent.log; then
    cat dumpevent.log
  fi
done < files.list
```

Ran on `hps-java:master` with `hps-mc:374-alignment-workflow`.

### Directory of FEE Skim
These files were produced by skimming the data above for the events collected due
to the FEE trigger[^#].
```
/sdf/group/hps/data/physrun2016/skim/goldenFees
```
There is also a file `goldenFeeSkimEvenly.slcio`
> which is intended to provide even coverage over the face of the ECal.
> This selects the same number of events per cluster seed crystal index. 
> This should allow one to, for instance, disambiguate between a simple Tu 
> and a combination of Tu+Rw by populating the edges of the sensors at large |v|.


[^#]: Waiting on Norman to confirm the details of this skim.


### Intial Detector
I created the zero'th iteration by copying the compact from the previous fully-aligned detector and setting all the millepede constants to zero.
`HPS-PhysicsRun2016-Pass2` was the original detector and this process created `HPS-PhysicsRun2016-KF-iter0`.

### General Plan
Following PF's outline from the [Spring 2023 Alignment Workshop](https://indico.slac.stanford.edu/event/7954/timetable/?view=standard) but cannot use full module parameters since those aren't available for the 2016 detector.

1. tu L345
2. tu L345
3. tu L345
4. tu+rw L1-L2
    - dangerous, should probably skip
6. tu+rw L5-L6
7. tu+rw L3-L4
8. ...something else?
