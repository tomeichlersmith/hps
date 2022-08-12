# Batch HPS at SLAC
Slurm copies the environment by default, so if we are in `[hps]` environment,
we can simply run `hpstr` prepended with `srun` to dispatch it to a worker node.

Putting each different "cluster" of jobs into its own directory is nice to separate
out any job log files produced during running. The general slurm submission file
that I will use a lot involves looping over a bash array of files.

```bash
#!/bin/bash
#
#SBATCH --partition=shared
#SBATCH --ntasks=1
#SBATCH --output=output-%j.txt
#
#SBATCH --job-name=tpt-ana
#
# Array defines the numbers uses in SLURM_ARRAY_TASK_ID
#   here we are using them as indices in a bash array of input files
# We could also use them as the run numbers since the files can be
#  constructed from the run number
#SBATCH --array=0-19

input_files=(${HPS_HOME}/2016-subsample/tuples/*)

srun hpstr ${HPS_HOME}/hist_cfg.py -i ${input_files[$SLURM_ARRAY_TASK_ID]} -t 1
```

Another helpfu slurm feature is job dependency `--dependency` which we could use
to automatically run analyses after a re-tuplization.

## Table of Contents
|- tpt        : Three Prong Tridents
   |- tuplize : tuplization from slcio files
   |- ana     : run TPT histogramming in hpstr
