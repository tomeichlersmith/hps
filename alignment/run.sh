
__usage__() {
  cat <<\HELP
    
    Run the tracking (both KF and GBL) over both iterations of the 2019SensorSurvey detector

  USAGE:
    
    ./run.sh

HELP
}

__run__() {
  local trk=$1
  local iter=$2

  local steering=alignmentDriver_chi2.lcsim
  if [ "${trk}" = "gbl" ]; then
    steering=gbl_tracking.lcsim
  fi

  java \
    -DdisableSvtAlignmentConstants \
    -XX:+UseSerialGC \
    -Xmx5000m \
    -jar /export/scratch/users/eichl008/hps/java/distribution/target/hps-distribution-5.1-SNAPSHOT-bin.jar \
    -R 10716 \
    -d HPS_Nominal_2019SensorSurvey_${iter} \
    -DoutputFile=${trk}_${iter} \
    ${steering} \
    -i fee_recon_20um120nA_200.slcio
  return $?
}

__main__() {
  case $1 in
    -h|--help|help|-?)
      __usage__
      return 0
      ;;
  esac

  for iter in iter{0,1}; do
    for trk in gbl kf; do
      __run__ ${trk} ${iter} &> ${trk}_${iter}_run.log &
    done
  done
  wait
}

__main__ $@
