
# Setup HPS and HPS-MC
```
cd /sdf/group/hps/users/
mkdir $USER
cd $USER
git clone git@github.com:tomeichlersmith/hps
git clone git@github.com:jeffersonlab/hps-mc hps/mc
wget https://github.com/JeffersonLab/hps-java/releases/download/hps-java-5.0/hps-distribution-5.0-bin.jar
```

# Install SLIC
```
git clone git@github.com:slaclab/slic
cd slic
source /sdf/group/hps/packages/setup_dt8.sh
cmake -B build -S . -DCMAKE_INSTALL_PREFIX=install
make install
```

