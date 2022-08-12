#!/bin/bash
#
#SBATCH --partition=shared
#SBATCH --ntasks=1
#SBATCH --output=%A-%a.out
#
# maximum job time of six hours
#SBATCH --time 6:00:00
# maximum job memory
#SBATCH --mem=8G
#
#SBATCH --job-name=tpt-tuplize
#
# the 2016-subsample Cam made available for me is
#   Run 007800 Partitions 0 - 387 (inclusive)
#SBATCH --array=0-387

hps_2016_subsample_data_dir=/sdf/group/hps/data/physrun2016/hps_007800/reco/hash8d32e68be1b/

srun hpstr ${HPS_HOME}/tuplize_cfg.py -t 1 \
  -i ${hps_2016_subsample_data_dir}/hps_007800_${SLURM_ARRAY_TASK_ID}.slcio \
  -d ${HPS_HOME}/2016-subsample/tuples/
