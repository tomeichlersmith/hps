# 2016 Alignment

Studying how updated Kalman Filter (KF) track finding effects the 2016 alignment.
Can we improve it?

*Table of Contents*
- `pede`: template directory for running pede via hps-mc
- `tracking`: template directory for running batch tracking via hps-mc
  - includes steering file used for hps-java

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

### Intial Detector
I created the zero'th iteration by copying the compact from the previous fully-aligned detector and setting all the millepede constants to zero.
`HPS-PhysicsRun2016-Pass2` was the original detector and this process created `HPS-PhysicsRun2016-KF-iter0`.

### General Plan
Following PF's outline from the [Spring 2023 Alignment Workshop](https://indico.slac.stanford.edu/event/7954/timetable/?view=standard) but cannot use full module parameters since those aren't available for the 2016 detector.

1. tu L345
2. tu L345
3. tu L345
4. tu+rw L1-L2
5. tu+rw L5-L6
6. tu+rw L3-L4
7. ...something else?
