#!/bin/bash

# FEMU - Free & Easy Mining on Ubuntu
#
# AMD GPU overclocking tool
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

if [ $1 = "--kernel" ]; then
	apt-add-repository -y ppa:teejee2008/ppa
	apt update
	apt install ukuu -y
	ukuu --install v4.17
fi

if [ $1 = "--install" ]; then
	apt install amdgpu-oc-systemd -y
fi

if [ $1 = "--cleargpu" ]; then
	touch /etc/miners/amdoverclock1.bash
	grep -Ev "\#GPU$2$" /etc/miners/amdoverclock.bash > /tmp/amdoverclock1.bash
	rm /etc/miners/amdoverclock.bash
	mv /tmp/amdoverclock1.bash /etc/miners/amdoverclock.bash
fi