#!/bin/bash
if [ $1 = "--kernel" ]; then
apt-add-repository -y ppa:teejee2008/ppa
apt update
apt install ukuu -y
ukuu --install v4.17
fi
if [ $1 = "--download" ]; then
cd /usr/src
apt install build-essential git
git clone https://github.com/OhGodACompany/OhGodATool
git clone https://github.com/RadeonOpenCompute/ROC-smi
fi
if [ $1 = "--install" ]; then
cd /usr/src/OhGodATool
make -j$(nproc)
ln -s /usr/src/OhGodATool/ohgodatool /usr/bin/ohgodatool
ln -s /usr/src/ROC-smi/rocm-smi /usr/bin/rocm-smi
fi
if [ $1 = "--cleargpu" ]; then
cd /opt
touch amdoverclock1.bash
grep -Ev "\#GPU$2$" amdoverclock.bash > amdoverclock1.bash
rm amdoverclock.bash
mv amdoverclock1.bash amdoverclock.bash
rm amdoverclock1.bash
fi