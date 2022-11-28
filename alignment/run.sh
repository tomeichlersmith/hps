
__usage__() {
  cat <<\HELP
    
    Run the tracking (both KF and ST) over the nominal and intentionally misaligned 2019 detectors.

  USAGE:
    
    bash run.sh [-h|--help|help|-?] TAG

  ARGUMENTS:
    TAG : short string to identify this run of tracking and mille

  OPTIONS:
    -h, --help, help, -? : Print this and exit

HELP
}

__run__() {
  local trk=$1
  local det=$2
  local tag=$3

  java \
    -DdisableSvtAlignmentConstants \
    -XX:+UseSerialGC \
    -Xmx5000m \
    -jar /export/scratch/users/eichl008/hps/java/distribution/target/hps-distribution-5.2-SNAPSHOT-bin.jar \
    -R 10716 \
    -d ${det}_${trk} \
    -DoutputFile=${trk}/${det}/${tag} \
    tracking_${trk}_alignment.lcsim \
    -i fee_recon_20um120nA_200.slcio
  return $?
}

__main__() {
  local tag=""
  case $1 in
    -h|--help|help|-?)
      __usage__
      return 0
      ;;
    -*)
      echo "ERROR: Unrecognized option '$1'"
      return 1
      ;;
    *)
      tag="$1"
      ;;
  esac

  if [ -z ${tag} ]; then
    echo "ERROR: Need to provide tag to distinguish this run."
    return 1
  fi

  dets=( HPS_2019_L1ty100um_iter4 HPS_2019_L1ty100um_iter5 )
  trks=( st kf )

  for i in "${!dets[@]}"; do
    det=${dets[$i]}
    trk=${trks[$i]}
    echo -n "$(date) ${trk} ${det} ..."
    mkdir -p ${trk}/${det} 
    __run__ ${trk} ${det} ${tag} &> ${trk}/${det}/${tag}_run.log
    echo "done"
  done
}

__main__ $@
