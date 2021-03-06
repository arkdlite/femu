#!/usr/bin/env python3

'''
 FEMU - Free & Easy Mining on Ubuntu

    Copyright 2018      Arkadii Chekha <arkdlite@protonmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import gi

from gi.repository import Gio
from os import path


class config():
    DIR = path.dirname(path.abspath(__file__))
    res = Gio.Resource.load("/usr/share/femu/resources/res.gresource")
