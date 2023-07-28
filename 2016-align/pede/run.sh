#!/usr/bin/scl enable devtoolset-8 -- /bin/bash
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --partition=shared

work_root="/sdf/group/hps/users/eichl008/hps/2016-align"
detname="$1"
find ${work_root}/${detname}/tracking/ -type f -name "*.bin" > ${detname}/pede/mille-bin.list || return $?
hps-mc-job run \
  -d ${work_root}/${detname}/pede/scratch \
  -c ${work_root}/pede/run.cfg \
  pede ${work_root}/${detname}/pede/job.json
