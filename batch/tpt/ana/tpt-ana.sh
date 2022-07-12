#!/bin/bash
#
#SBATCH --partition=shared
#SBATCH --ntasks=1
#SBATCH --output=%A-%a.out
#
# Filename Pattern Quick Ref:
#   %J - job id number (universal)
#   %a - array number
#   %A - master number for arrays
#
#SBATCH --job-name=tpt-ana
#
# the 2016-subsample Cam made available for me is
#   Run 007800 Partitions 0 - 387 (inclusive)
# we could change this to be something defined on the comand line
#SBATCH --array=0-20

srun hpstr ${HPS_HOME}/hist_cfg.py -t 1 \
  -i ${HPS_HOME}/2016-subsample/tuples/tuple_2016_subsample_run_007800_part_$(printf "%04d" ${SLURM_ARRAY_TASK_ID}).root
