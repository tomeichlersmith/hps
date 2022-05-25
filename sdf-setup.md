
# Setup HPS SW
```bash
cd /sdf/group/hps/users/
mkdir $USER
cd $USER
git clone git@github.com:tomeichlersmith/hps
git clone git@github.com:jeffersonlab/hps-mc hps/mc
git clone git@github.com:jeffersonlab/hps-java hps/java
git clone git@github.com:jeffersonlab/hps-lcio hps/lcio
cd hps
cp /sdf/group/hps/users/bravo/setup/bashrc.sh .
# copy .hpsmc text into file called hpsmc in this directory
source bashrc.sh # saw some errors, will need to update it
cd java
mvncbld # alias from bashrc.sh
cd ../lcio
mvnclbd
```

Need a newere cmake for hps-mc
```
python3 -m pip install --user --upgrade cmake
```

Using Cams GSL
```
/sdf/group/hps/users/bravo/src/gsl-2.6/install
```

Built hps-mc with
```
cd mc
source ../bashrc.sh
cmake -B build -S . \
  -DHPSMC_ENABLE_EGS5=ON \
  -DHPSMC_ENABLE_MADGRAPH=OFF \
  -DHPSMC_ENABLE_STDHEP=ON \
  -DHPSMC_ENABLE_FIELDMAPS=ON \
  -DHPSMC_ENABLE_LCIO=ON \
  -DHPSMC_ENABLE_HPSJAVA=ON \
  -DHPSMC_ENABLE_CONDITIONS=OFF
  -DGSL_ROOT_DIR=${GSL_ROOT_DIR} \
  -DCMAKE_INSTALL_PREFIX=install
cd build
make install
```

## Test
Run example tritrig simulation.
```
cd hps/mc/examples/tritrig
hps-mc-job run -d scratch tritrig job.json
```

## hpstr
Need LCIO and ROOT.
```
cd hps/lcio
cmake -B build -S . -DCMAKE_INSTALL_PREFIX=install
cd build
cp ../LCIOLibDeps.cmake .
make install
```
Using Cams ROOT.
