
__usage__() {
  cat <<\HELP
    
    Run the tracking (both KF and GBL) over both iterations of the 2019SensorSurvey detector

  USAGE:
    
    ./run.sh

HELP
}

__run__() {
  local trk=$1
  local det=$2

  java \
    -DdisableSvtAlignmentConstants \
    -XX:+UseSerialGC \
    -Xmx5000m \
    -jar /export/scratch/users/eichl008/hps/java/distribution/target/hps-distribution-5.1-SNAPSHOT-bin.jar \
    -R 10716 \
    -d ${det} \
    -DoutputFile=${trk}/${det}/${trk}_${det} \
    tracking_${trk}_alignment.lcsim \
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

  for det in HPS_Nominal_2019SensorSurvey_iter0 HPS_2019_L1ty100um_iter0; do
    for trk in gbl kf; do
      echo -n "${trk} ${det} ..."
      mkdir -p ${trk}/${det} 
      __run__ ${trk} ${det} &> ${trk}/${det}/${trk}_${det}_run.log
      echo "done"
    done
  done
}

__main__ $@
