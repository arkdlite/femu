#!/usr/bin/env python3

'''
 FEMU - Free & Easy Mining on Ubuntu

 GPU Driver installer
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

import os, gi

from threading import Thread
from gi.repository import Gtk, Gio, GdkPixbuf
from .femu_config import config

class Params():
    reboot = False  # variable for Params.reboot
    amd = False
    nvidia = False
    DIR = os.path.dirname(os.path.realpath(__file__))
    amdprogressbar = Gtk.ProgressBar()
    nvprogressbar = Gtk.ProgressBar()

class DialogWindow(Gtk.Dialog):  # error window
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Error!", parent, 0,
        (Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label("You haven't selected any driver!")

        box = self.get_content_area()
        box.add(label)
        self.show_all()

class RebootWindow(Gtk.Window):
    def __init__(self, parent):
        Gtk.Window.__init__(self, title="Driver installation")
        self.set_border_width(10)

        self.set_default_size(150, 100)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_homogeneous(False)
        self.add(box)
        label = Gtk.Label("Driver have been installed. Please, Params.reboot the computer.")
        box.pack_start(label, True, True, 0)
        self.button = Gtk.Button(label="Params.reboot")
        self.button.connect("clicked", self.on_button_clicked)
        box.pack_start(self.button, True, True, 0)

    def on_button_clicked(self, button):
        os.system("Params.reboot")

class InstallNvidiaWindow(Gtk.Window):
    def __init__(self, parent):
        Gtk.Window.__init__(self, title="Driver installation")
        self.set_border_width(10)

        self.set_default_size(150, 100)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_homogeneous(False)
        self.add(box)
        label = Gtk.Label()
        label.set_text("""The newest version of Nvidia driver will be added to
                repositories list. Than the default Ubuntu tool will be
                opened. To start installation please click 'Additional
                drivers'. Next choose the newest version of Nvidia driver
                and install this. After that reboot this computer.""")
        box.pack_start(label, True, True, 0)
        Params.nvprogressbar = Gtk.ProgressBar()
        box.pack_start(Params.nvprogressbar, True, True, 0)

        self.button = Gtk.Button(label="OK")
        self.button.connect("clicked", self.on_button_clicked)
        box.pack_start(self.button, True, True, 0)
        self.activity_mode = False

    def on_button_clicked(self, button):
        ProgressThread().start()
        self.button.set_sensitive(False)

class InstallAMDWindow(Gtk.Window):
    def __init__(self, parent):
        Gtk.Window.__init__(self, title="Driver installation")
        self.set_border_width(10)

        self.set_default_size(150, 100)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_homogeneous(False)
        self.add(box)
        label = Gtk.Label("The newest AMDGPU-PRO driver will be downloaded and installed.")
        box.pack_start(label, True, True, 0)
        Params.amdprogressbar = Gtk.ProgressBar()
        box.pack_start(Params.amdprogressbar, True, True, 0)

        self.button = Gtk.Button(label="Start")
        self.button.connect("clicked", self.on_button_clicked)
        box.pack_start(self.button, True, True, 0)
        self.activity_mode = False

    def on_button_clicked(self, button):
        ProgressThread().start()
        self.button.set_sensitive(False)

class LabelWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Driver installation")
        self.set_border_width(10)
        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hbox.set_homogeneous(False)
        label = Gtk.Label()
        label.set_markup("<big>Hello!</big>\n"
                  "This tool can help you with mining configuration\n"
                  "What drivers you want install?\n")
        label.set_justify(Gtk.Justification.FILL)
        hbox.pack_start(label, True, True, 0)

        vbox = Gtk.Box(spacing=6)
        vbox.set_homogeneous(False)
        hbox.pack_start(vbox, True, True, 0)

        label = Gtk.Label()
        label.set_markup("<big>Nvidia</big>\n")
        label.set_justify(Gtk.Justification.FILL)
        vbox.pack_start(label, True, True, 0)
        self.nvswitch = Gtk.Switch()
        self.nvswitch.connect("notify::active", self.on_nvidia_activated)
        self.nvswitch.set_active(False)
        vbox.pack_start(self.nvswitch, True, True, 0)

        label = Gtk.Label()
        label.set_markup("<big>AMD</big>\n")
        label.set_justify(Gtk.Justification.FILL)
        vbox.pack_start(label, True, True, 0)
        self.amdswitch = Gtk.Switch()
        self.amdswitch.connect("notify::active", self.on_amd_activated)
        self.amdswitch.set_active(False)
        vbox.pack_start(self.amdswitch, True, True, 0)

        mbox = Gtk.Box(spacing=6)
        mbox.set_homogeneous(False)
        hbox.pack_start(mbox, True, True, 0)


        self.button = Gtk.Button(label="Install!")
        self.button.connect("clicked", self.on_button_clicked)
        mbox.pack_start(self.button, True, True, 0)


        self.add(hbox)
    def on_nvidia_activated(self, switch, gparam):
        if switch.get_active():
            Params.nvidia = True
            self.amdswitch.set_active(False)
        else:
            Params.nvidia = False
    def on_amd_activated(self, switch, gparam):
        if switch.get_active():
            Params.amd = True
            self.nvswitch.set_active(False)
        else:
            Params.amd = False
    def on_button_clicked(self, button):
        if Params.amd == False and Params.nvidia == False:
            dialog = DialogWindow(self)
            dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            dialog.set_resizable(False)
            dialog.run()
            dialog.destroy()
        if Params.amd == True:
            install = InstallAMDWindow(self)
            install.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            install.set_resizable(False)
            install.show_all()
        if Params.nvidia == True:
            install = InstallNvidiaWindow(self)
            install.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            install.set_resizable(False)
            install.show_all()

class ProgressThread(Thread):  # install thread
    def run(self):
        if Params.amd == True:  # if Params.amd selected
            Params.amdprogressbar.set_fraction(0.01)  # setting progress to 1%
            Params.amdprogressbar.set_text("Downloading")
            os.system(Params.DIR + "/amdgpu-pro-install.bash --step1")

            Params.amdprogressbar.set_fraction(0.2)
            Params.amdprogressbar.set_text("Unpacking files")
            os.system(Params.DIR + "/amdgpu-pro-install.bash --step2")

            Params.amdprogressbar.set_fraction(0.4)
            Params.amdprogressbar.set_text("Running installation script")
            os.system(Params.DIR + "/amdgpu-pro-install.bash --step3")

            Params.amdprogressbar.set_fraction(1.0)
            Params.reboot = True

        if Params.nvidia == True:  # if Params.nvidia selected
            Params.nvprogressbar.set_fraction(0.5)
            os.system(Params.DIR + "/nvidia-current-install.bash")
            os.popen("software-properties-gtk")
            Params.nvprogressbar.set_fraction(1.0)
            Gtk.main_quit()



class DriverInstaller():
    Gio.Resource._register(config.res)

    window = LabelWindow()
    window.set_default_size(400, 60)
    window.set_icon(GdkPixbuf.Pixbuf.new_from_resource("/org/gtk/Femu/icons/icon.png"))
    window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    window.set_resizable(False)
    window.connect("destroy", Gtk.main_quit)
    
    def run(self): DriverInstaller.window.show_all()
