# alignment makefile
# 	simple aliases of common functions to avoid having
# 	to cd to a bunch of directories all the gd time

gbl:
	cd general-broken-lines/cpp/build/ubuntu && $(MAKE)

java:
	cd ${HOME}/java && mvn install -DskipTests -Dcheckstyle.skip

run:
	hps-mc-job run track_align single-accum-job.json -i 1
