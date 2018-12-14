#!/bin/bash

# FEMU - Free & Easy Mining on Ubuntu
#
# GPU Miner installer
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

if [ $1 = "--ethminer-bin" ]; then
	apt install ethminer
fi

if [ $1 = "--step2xmr" ]; then
	apt install xmrig-amd
fi

if [ $1 = "--ethminer-autostart" ]; then
	systemctl enable ethminer
fi