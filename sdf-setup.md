
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
