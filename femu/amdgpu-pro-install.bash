#!/bin/bash

# FEMU - Free & Easy Mining on Ubuntu
#
# GPU Driver installer
#    Copyright 2018      Arkadii Chekha <arkdlite@protonmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.

if [ $1 = "--step1" ]; then
	cd /tmp
	wget https://drivers.amd.com/drivers/linux/amdgpu-pro-18.40-676022-ubuntu-18.04.tar.xz --referer https://www.amd.com/en/support/kb/release-notes/rn-prorad-lin-18-40
fi

if [ $1 = "--step2" ]; then
	cd /tmp
	tar -xpJf amdgpu-pro-18.40-676022-ubuntu-18.04.tar.xz
fi

if [ $1 = "--step3" ]; then
	cd /tmp/amdgpu-pro-18.40*
	touch /var/log/amdgpu-pro.log
	./amdgpu-install -y --opencl=pal,legacy --headless >> /var/log/amdgpu-pro.log 2>&1
fi