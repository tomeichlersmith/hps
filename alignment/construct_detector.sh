__usage__() {
  cat <<\HELP

  Construct a detector LCDD file from the corresponding compact.xml.

 USAGE:
  bash /full/path/to/construct_detector.sh ITER TAG
 
  You need to be within the root directory of hps-java when
  this script is run. The directory of the detector we will
  be constructing is

    detector-data/detectors/HPS_<tag>_<iter>/

 ARGUMENTS:
  ITER : iteration of the detector tag that is being developed
  TAG  : tag for detector (usually related to year)
 
HELP
}

__main__() {
  iteration=$1
  tag=$2
  
  if [ "$#" -eq 0 ]; then
    __usage__;
    return 0;
  fi
  if [ "$#" -ne 2 ]; then
    echo "Did not provide the two (and only two) arguments: ITER TAG"
    return 1
  fi

  cd detector-data
  if ! java \
    -Dorg.lcsim.cacheDir=/externals \
    -cp ../distribution/target/hps-distribution-5.1-SNAPSHOT-bin.jar \
    org.hps.detector.DetectorConverter \
    -f lcdd \
    -i detectors/HPS_${tag}_$iteration/compact.xml \
    -o detectors/HPS_${tag}_$iteration/HPS_${tag}_$iteration.lcdd; then
    return $?
  fi
  
  echo "name: HPS_${tag}_$iteration" > detectors/HPS_${tag}_$iteration/detector.properties
  
  mvn -T 4 -DskipTests=true
  cd ..
  cd distribution
  mvn -T 4 -DskipTests=true
  cd ..
}

__main__ $@
