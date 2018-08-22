#!/bin/bash
if [ $1 = "--step1" ]; then
cd /tmp
wget https://www2.ati.com/drivers/linux/ubuntu/18.04/amdgpu-pro-18.30-633530.tar.xz --referer https://www.amd.com/en/support/kb/release-notes/rn-prorad-lin-18-30
fi
if [ $1 = "--step2" ]; then
cd /tmp
tar -xpJf amdgpu-pro-18.30-633530.tar.xz
fi
if [ $1 = "--step3" ]; then
cd /tmp/amdgpu-pro-18.30-633530
touch /var/log/amdgpu-pro.log
./amdgpu-install -y --opencl=pal,legacy > /var/log/amdgpu-pro.log
cd
fi

