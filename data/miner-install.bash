#!/bin/bash
if [ $1 = "--step1" ]; then
cd $2
rm -Rf miners
mkdir miners
fi

if [ $1 = "--ethminer-bin" ]; then
cd $2
wget https://github.com/ethereum-mining/ethminer/releases/download/v0.16.0.dev1/ethminer-0.16.0.dev1-Linux.tar.gz
tar -xvzf ethminer-0.16.0.dev1-Linux.tar.gz
mv bin ethminer
cd ethminer
mkdir build
mkdir build/ethminer
cp ethminer build/ethminer
cp -Rf kernels build/ethminer
fi

if [ $1 = "--ethminer-build" ]; then
touch /var/log/CLRX-build.log
touch /var/log/ethminer-build.log
cd $2
add-apt-repository -y ppa:ubuntu-toolchain-r/test
apt update
apt -y upgrade
apt install gcc-snapshot gcc-8 g++-8 make build-essential git mesa-common-dev cmake freeglut3 freeglut3-dev libpng-dev gcc-5 g++-5 -y
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 60 --slave /usr/bin/g++ g++ /usr/bin/g++-8
git clone https://github.com/ethereum-mining/ethminer.git
git clone https://github.com/CLRX/CLRX-mirror
cd CLRX-mirror
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DOPENCL_LIBRARY=/opt/amdgpu-pro/lib/x86_64-linux-gnu/libOpenCL.so > /var/log/CLRX-build.log
make -j$(nproc) > /var/log/ethminer-build.log
make install
cd $2
cd ethminer
git submodule update --init --recursive
mkdir build
cd libethash-cl/kernels/bin
rm ethash_*.bin
cd $2/ethminer/libethash-cl/kernels/isa
clrxasm -o ethash_baffin_lws64.bin --defsym=worksize='64' -g 'baffin' -b 'amdcl2' -A 'gcn1.4' GCN_ethash.isa
clrxasm -o ethash_baffin_lws128.bin --defsym=worksize='128' -g 'baffin' -b 'amdcl2' -A 'gcn1.4' GCN_ethash.isa
clrxasm -o ethash_baffin_lws192.bin --defsym=worksize='192' -g 'baffin' -b 'amdcl2' -A 'gcn1.4' GCN_ethash.isa
clrxasm -o ethash_baffin_lws256.bin --defsym=worksize='256' -g 'baffin' -b 'amdcl2' -A 'gcn1.4' GCN_ethash.isa
clrxasm -o ethash_ellesmere_lws64.bin --defsym=worksize='64' -g 'ellesmere' -b 'amdcl2' -A 'gcn1.4' GCN_ethash.isa
clrxasm -o ethash_ellesmere_lws128.bin --defsym=worksize='128' -g 'ellesmere' -b 'amdcl2' -A 'gcn1.4' GCN_ethash.isa
clrxasm -o ethash_ellesmere_lws192.bin --defsym=worksize='192' -g 'ellesmere' -b 'amdcl2' -A 'gcn1.4' GCN_ethash.isa
clrxasm -o ethash_ellesmere_lws256.bin --defsym=worksize='256' -g 'ellesmere' -b 'amdcl2' -A 'gcn1.4' GCN_ethash.isa
clrxasm -o ethash_gfx901_lws64.bin --defsym=worksize='64' -g 'gfx901' -b 'amdcl2' -A 'gcn1.5' GCN_ethash.isa
clrxasm -o ethash_gfx901_lws128.bin --defsym=worksize='128' -g 'gfx901' -b 'amdcl2' -A 'gcn1.5' GCN_ethash.isa
clrxasm -o ethash_gfx901_lws192.bin --defsym=worksize='192' -g 'gfx901' -b 'amdcl2' -A 'gcn1.5' GCN_ethash.isa
clrxasm -o ethash_gfx901_lws256.bin --defsym=worksize='256' -g 'gfx901' -b 'amdcl2' -A 'gcn1.5' GCN_ethash.isa
clrxasm -o ethash_tonga_lws64.bin --defsym=worksize='64' -g 'tonga' -b 'amdcl2' -A 'gcn1.1' GCN_ethash.isa
clrxasm -o ethash_tonga_lws128.bin --defsym=worksize='128' -g 'tonga' -b 'amdcl2' -A 'gcn1.1' GCN_ethash.isa
clrxasm -o ethash_tonga_lws192.bin --defsym=worksize='192' -g 'tonga' -b 'amdcl2' -A 'gcn1.1' GCN_ethash.isa
clrxasm -o ethash_tonga_lws256.bin --defsym=worksize='256' -g 'tonga' -b 'amdcl2' -A 'gcn1.1' GCN_ethash.isa
cp ethash_*.bin $2/ethminer/libethash-cl/kernels/bin
cd $2/ethminer/build
cmake .. -DETHASHCUDA=OFF > /var/log/ethminer-build.log
cmake --build . > /var/log/ethminer-build.log
fi

if [ $1 = "--step1xmr" ]; then
add-apt-repository -y ppa:ubuntu-toolchain-r/test
apt update
apt -y upgrade
apt install git build-essential make cmake libuv1-dev gcc-snapshot gcc-8 g++-8 libmicrohttpd-dev opencl-c-headers -y
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 60 --slave /usr/bin/g++ g++ /usr/bin/g++-8
fi

if [ $1 = "--step2xmr" ]; then
cd $2
git clone https://github.com/xmrig/xmrig-amd.git
cd xmrig-amd
mkdir build
fi

if [ $1 = "--devfeeoff" ]; then
rm $2/xmrig-amd/src/donate.h
cp off.h $2/xmrig-amd/src
mv $2/xmrig-amd/src/off.h $2/xmrig-amd/src/donate.h
fi

if [ $1 = "--step3xmr" ]; then
touch /var/log/xmrig-amd-build.log
cd $2/xmrig-amd/build
cmake .. -DOPENCL_LIBRARY=/opt/amdgpu-pro/lib/x86_64-linux-gnu/libOpenCL.so -DOpenCL_INCLUDE_DIR=/opt/amdgpu-pro/lib/x86_64-linux-gnu > /var/log/xmrig-amd-build.log
fi

if [ $1 = "--step4xmr" ]; then
cd $2/miners/xmrig-amd/build
make -j$(nproc) > /var/log/xmrig-amd-build.log
cp $2/miners/xmrig-amd/build/xmrig-amd $2/miners/xmrig-amd
fi

if [ $1 = "--step2" ]; then
touch $2
chmod 777 $2
chmod ugo+x $2
cd
fi
