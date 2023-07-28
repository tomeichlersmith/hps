#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --partition=shared
#SBATCH --output=output/logs/%A-%a.out

work_root="/sdf/group/hps/users/eichl008/hps"
idm_dir="${work_root}/idm/reach/2016"
job="$1"
job_list="$2"
job_id="${SLURM_ARRAY_TASK_ID}"
srun \
  hps-mc-job \
    run \
    -c ${work_root}/hpsmc \
    -c ${idm_dir}/batch.cfg \
    -d /scratch/$USER/batch/${job_id} \
    ${job} \
    ${job_list} \
    -i ${job_id}
