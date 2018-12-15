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

import sys
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf, Gio
from os import popen, path
from .nvidia_oc import NvidiaOC
from .femu_config import config
from .miner_installer import MinerInstaller
from .driver_installer import DriverInstaller

Gio.Resource._register(config.res)  # register gresource file with icon


class MenuWindow(Gtk.Window):
    icon = GdkPixbuf.Pixbuf.new_from_resource("/org/gtk/Femu/icons/icon.png")

    def __init__(self):
        Gtk.Window.__init__(self, title="FEMU - Free & Easy Mining on Ubuntu")
        self.set_border_width(10)
        self.set_icon(self.icon)
        self.set_default_size(150, 100)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_homogeneous(False)

        self.buttondriver = Gtk.Button(label="Drivers installation")
        self.buttondriver.connect("clicked", self.on_buttondriver_clicked)
        box.pack_start(self.buttondriver, True, True, 0)

        self.buttonminer = Gtk.Button(label="Miners installation")
        self.buttonminer.connect("clicked", self.on_buttonminer_clicked)
        box.pack_start(self.buttonminer, True, True, 0)

        self.buttonamdoc = Gtk.Button(label="Nvidia Overclocking")
        self.buttonamdoc.connect("clicked", self.on_buttonamdoc_clicked)
        box.pack_start(self.buttonamdoc, True, True, 0)

        self.buttonabout = Gtk.Button(label="About")
        self.buttonabout.connect("clicked", self.on_abtdlg)
        box.pack_start(self.buttonabout, True, True, 0)

        self.add(box)

    def on_buttonamdoc_clicked(self, button):
        NvidiaOC.run(self)  # run Nvidia OC window

    def on_buttondriver_clicked(self, button):
        DriverInstaller.run(self)

    def on_buttonminer_clicked(self, button):
        MinerInstaller.run(self)

    def on_abtdlg(self, button):
        about = Gtk.AboutDialog(self)
        about.set_logo(self.icon)
        about.set_program_name("FEMU - Free & Easy Mining on Ubuntu")
        about.set_version("v0.3 alpha")
        about.set_copyright("© arkdlite 2018")
        about.set_comments("""This tool was created for easy configuration Ubuntu
        for cryptocurrency mining without any difficulties
        for miners-beginners. If you find this program
        useful, you can make a donation for author. Thanks!
        BTC: 1DtJutLDmH1MzY7Ew36ziLPp3YNuwXpvfb
        DASH: XqMYsGQyLGzr76cQXd7LHD6VEi13xRnm47
        ZEC: t1eFez4MmkQALbhEGSFLcLERCZT3MM7KFQB
        XMR: 421cec4uww4hRKZUrmbxRBhTPqRXmb6PCFcyuakwmdr3ThcanQtoqQCPHSAWC4PPZfjAN6tt5yx7rSQf25SyTKhdFcsBaWK""")
        about.run()
        about.destroy()


class Start():
    window = MenuWindow()  # main window
    window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    window.set_resizable(False)
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
