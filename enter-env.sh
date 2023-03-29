apptainer run \
  --env "PS1=${PS1}" \
  --env "LS_COLORS=${LS_COLORS}" \
  --hostname hps-env.$(uname -n) \
  --home /export/scratch/users/eichl008/hps \
  ${1:-hps-env-v2.0.0.sif} \
  /bin/bash -i # make shell interactive
