#!/bin/bash
#
#SBATCH --partition=shared
#SBATCH --ntasks=1
#SBATCH --output=output-%j.txt
#
#SBATCH --job-name=tpt-tuplize
#
# the 2016-subsample Cam made available for me is
#   Run 007800 Partitions 0 - 387 (inclusive)
#SBATCH --array=0-19

hps_2016_subsample_data_dir=${HPS_HOME}/2016-subsample/reco/

srun hpstr ${HPS_HOME}/tuplize_cfg.py -t 1 \
  -i ${hps_2016_subsample_data_dir}/hps_007800_${SLURM_ARRAY_TASK_ID}.slcio \
  -d ${HPS_HOME}/2016-subsample/tuples/
