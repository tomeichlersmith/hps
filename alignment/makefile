# alignment makefile
# 	simple aliases of common functions to avoid having
# 	to cd to a bunch of directories all the gd time

config-gbl:
	cd general-broken-lines/cpp && cmake -B build -S . -DSUPPORT_ROOT=OFF

gbl:
	cd general-broken-lines/cpp/build && $(MAKE)

java:
	cd ${HOME}/java && mvn install -DskipTests -Dcheckstyle.skip

# run the tests if offline mode ('-o')
# 	otherwise maven will check with central repositories to see if dependencies need to be updated
# 	this is a waste of time in this case where we are quickly running many times
test:
	cd ${HOME}/java/tracking &&\
	mvn \
		-o \
		-Djna.library.path=${HOME}/alignment/general-broken-lines/cpp/build/lib \
		-Dtest=GblJNA \
		test

run: 
	#hps-mc-job run track_align single-accum-job.json -i 1
	java \
		-Xmx5000m \
		-XX:+UseSerialGC \
		-Djna.library.path=/export/scratch/users/eichl008/hps/alignment/general-broken-lines/cpp/build/lib/ \
		-jar /export/scratch/users/eichl008/hps/.m2/repository/org/hps/hps-distribution/5.2-SNAPSHOT/hps-distribution-5.2-SNAPSHOT-bin.jar \
		-R 10666 \
		-d L3TStereo_tu_50um_iter0 \
		-D outputFile=events_kf_mille \
		/export/scratch/users/eichl008/hps/mc/examples/alignment/tracking/tracking_kf_alignment.lcsim \
		-i events.slcio
