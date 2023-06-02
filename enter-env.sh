singularity run \
  --env "PS1=${PS1}" \
  --env "LS_COLORS=${LS_COLORS}" \
  --bind /sdf/group/hps \
  --hostname hps-env.$(uname -n) \
  --home $(pwd -P) \
  ${1:-hps-env-v3.0.0.sif} \
  /bin/bash -i # make shell interactive
