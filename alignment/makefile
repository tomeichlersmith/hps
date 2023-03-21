# alignment makefile
# 	simple aliases of common functions to avoid having
# 	to cd to a bunch of directories all the gd time

config-gbl:
	cd general-broken-lines/cpp && cmake -B build -S .

gbl:
	cd general-broken-lines/cpp/build && $(MAKE)

java:
	cd ${HOME}/java && mvn install -DskipTests -Dcheckstyle.skip

run: 
	hps-mc-job run track_align single-accum-job.json -i 1

test:
	cd ${HOME}/java/tracking && mvn -Djna.library.path=${HOME}/alignment/general-broken-lines/cpp/build/lib -Dtest=GblJNA test
