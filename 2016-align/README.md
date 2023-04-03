# 2016 Alignment

Studying how updated Kalman Filter (KF) track finding effects the 2016 alignment.
Can we improve it?

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

