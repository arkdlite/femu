#!/usr/bin/env python3

'''
 FEMU - Free & Easy Mining on Ubuntu

 GPU Miner installer
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
import os

from threading import Thread
from gi.repository import Gtk, GLib, Gio, GdkPixbuf
from .femu_config import config


class Params():
    # variables for Ethminer parameters
    ethminer = False
    eparams = "-X --farm-recheck 200 stratum://0x012345678901234567890234567890123@nanopool.org:9999/miner1/example@gmail.com"
    ELABEL = """You are editing Ethminer configuration.
    Please check how to configure ethminer on
    your mininng pool. PLEASE, REMOVE 'ethminer.exe' OR
    './ethminer' THE FROM CONFIG!!! You are editing:"""

    # variables for XMRig-AMD parameters
    xmrig = False
    xparams = """{
    "algo": "cryptonight",
    "api": {
        "port": 3334,
        "access-token": null,
        "worker-id": "worker",
        "ipv6": false,
        "restricted": true
    },
    "background": false,
    "colors": true,
    "donate-level": 1,
    "log-file": null,
    "opencl-platform": "AMD",
    "pools": [
        {
            "url": "pool.com:1337",
            "user": "username",
            "pass": "password",
            "keepalive": true,
            "nicehash": false,
            "variant": -1,
            "tls": false,
            "tls-fingerprint": null
        }
    ],
    "print-time": 30,
    "retries": 5,
    "retry-pause": 5,
    "syslog": true,
    "threads": null
    }"""
    XLABEL = """Please copy the configuration from https://config.xmrig.com/
    for AMD Linux miner in JSON format. Don't forget to set '3334'
    API port!!! You are editing:"""

    errortext = ""  # variable for error text for dialog
    errorhead = "Error!"  # variable for header for dialog
    progr = 0.0  # variable for progressbar percentage
    progrtext = ""  # variable for progressbar text
    dialrun = False  # variable for dialog running
    builder = Gtk.Builder.new_from_resource("/org/gtk/Femu/glade/miner_config_window.glade")


def runcmd(cmd):
    os.system(cmd + " >> /var/log/femu.log 2>&1")


class SignalEthminer:
    def onDestroy(self, *args):
        print("Configuration saved")

    def ButtonClicked(self, button):
        SaveThreadEthminer().run()


class SaveThreadEthminer(Thread):
    def run(self):
        textbuffer = Params.builder.get_object("textbuffer")

        start_iter = textbuffer.get_start_iter()
        end_iter = textbuffer.get_end_iter()
        Params.eparams = textbuffer.get_text(start_iter, end_iter, True)
        Params.eparams += " --api-bind 3333"
        Params.configwindow.destroy()


class SaveThreadXmrig(Thread):
    def run(self):
        textbuffer = Params.builder.get_object("textbuffer")

        start_iter = textbuffer.get_start_iter()
        end_iter = textbuffer.get_end_iter()
        Params.xparams = textbuffer.get_text(start_iter, end_iter, True)

        Params.configwindow.destroy()


class SignalXmrig:
    def onDestroy(self, *args):
        print("Configuration saved")

    def ButtonClicked(self, button):
        SaveThreadXmrig().run()


class ProgressThread(Thread):  # class for scripts running
    def run(self):
        InstallMinerWindow.progressbar.set_fraction(0.05)
        InstallMinerWindow.progressbar.set_text("Running the installation")

        if Params.ethminer is True:  # if Ethminer activated
            runcmd("apt install ethminer-systemd -y")
            InstallMinerWindow.progressbar.set_fraction(0.9)
            runcmd("touch /etc/miners/ethminer.conf")
            runcmd("echo '%s' > /etc/miners/ethminer.conf" % Params.eparams)
            InstallMinerWindow.progressbar.set_fraction(1.0)

        if Params.xmrig is True:  # if XMRig-AMD activated
            InstallMinerWindow.progressbar.set_fraction(0.01)
            InstallMinerWindow.progressbar.set_text("Installing packages")
            runcmd("apt install xmrig-amd -y")
            InstallMinerWindow.progressbar.set_fraction(0.9)
            runcmd("touch /usr/bin/config.json")
            runcmd("ln -s /usr/bin/config.json /etc/miners/xmrig-amd.json")
            runcmd("echo '%s' > /etc/miners/xmrig-amd.json" % Params.xparams)
            runcmd("systemctl enable xmrig-amd")
            InstallMinerWindow.progressbar.set_fraction(1.0)

        # dialog for finish installation
        Params.errorhead = "Success!"
        Params.errortext = """Software for mining has been installed.
        All miners were added to autostart script.
        To see your hashrate run: sudo screen -r (miner)
        Good luck!
        Press 'OK' to quit."""
        Params.dialrun = True


class DialogWindow(Gtk.Dialog):  # dialog window
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, Params.errorhead, parent, 0,  # header
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label(Params.errortext)  # window text

        box = self.get_content_area()
        box.add(label)
        self.show_all()


class InstallMinerWindow(Gtk.Window):  # miners install window
    progressbar = Gtk.ProgressBar()

    def __init__(self, parent):
        Gtk.Window.__init__(self, title="Miners installation")
        self.set_border_width(10)

        self.set_default_size(150, 100)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_homogeneous(False)
        self.add(box)
        label = Gtk.Label("The newest miners will be installed now.")
        box.pack_start(label, True, True, 0)
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(True)
        box.pack_start(self.progressbar, True, True, 0)

        self.buttonstart = Gtk.Button(label="Start!")
        self.buttonstart.connect("clicked", self.on_buttonstart_clicked)
        box.pack_start(self.buttonstart, True, True, 0)
        self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
        self.activity_mode = False

    def on_timeout(self, user_data):  # edit progresspar on timeout
        if Params.dialrun is True:
            dialog = DialogWindow(self)
            dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            dialog.set_resizable(False)
            dialog.run()
            dialog.destroy()
            quit()  # quit after dialog was closed
        return True

    def on_buttonstart_clicked(self, button):  # starting installation thread
        ProgressThread().start()
        self.buttonstart.set_sensitive(False)


class MainWindow(Gtk.Window):  # main window
    def __init__(self):
        Gtk.Window.__init__(self, title="Miners installation")
        self.set_border_width(10)
        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hbox.set_homogeneous(False)
        label = Gtk.Label()
        label.set_markup("""<big>Hello!</big>
                         This tool will help you with mining configuration."
                         Please, configure miners before installation!"
                         What miners you want install?"""
                         )
        label.set_justify(Gtk.Justification.FILL)
        hbox.pack_start(label, True, True, 0)

        vbox = Gtk.Box(spacing=6)
        vbox.set_homogeneous(False)
        hbox.pack_start(vbox, True, True, 0)

        label = Gtk.Label()
        label.set_markup("<big>  Ethminer  </big>\n")
        label.set_justify(Gtk.Justification.FILL)
        vbox.pack_start(label, True, True, 0)
        self.ethswitch = Gtk.Switch()
        self.ethswitch.connect("notify::active", self.on_ethminer_activated)
        self.ethswitch.set_active(False)
        vbox.pack_start(self.ethswitch, True, True, 0)

        self.button = Gtk.Button(label="Config")
        self.button.connect("clicked", self.on_ethconf_clicked)
        self.button.set_sensitive(False)
        vbox.pack_start(self.button, True, True, 0)

        qbox = Gtk.Box(spacing=6)
        qbox.set_homogeneous(False)
        hbox.pack_start(qbox, True, True, 0)

        label = Gtk.Label()
        label.set_markup("<big>XMRig-AMD</big>\n")
        label.set_justify(Gtk.Justification.FILL)
        qbox.pack_start(label, True, True, 0)
        self.xmrswitch = Gtk.Switch()
        self.xmrswitch.connect("notify::active", self.on_xmrig_activated)
        self.xmrswitch.set_active(False)
        qbox.pack_start(self.xmrswitch, True, True, 0)

        self.button2 = Gtk.Button(label="Config")
        self.button2.connect("clicked", self.on_xmrconf_clicked)
        self.button2.set_sensitive(False)
        qbox.pack_start(self.button2, True, True, 0)

        wbox = Gtk.Box(spacing=6)
        wbox.set_homogeneous(False)
        hbox.pack_start(wbox, True, True, 0)

        self.button1 = Gtk.Button(label="Install!")
        self.button1.connect("clicked", self.on_button1_clicked)
        hbox.pack_start(self.button1, True, True, 0)

        self.add(hbox)

    def on_ethminer_activated(self, switch, gparam):
        if switch.get_active():
            Params.ethminer = True
            self.button.set_sensitive(True)
        else:
            Params.ethminer = False
            self.button.set_sensitive(False)

    def on_ethconf_clicked(self, button):

        Params.configwindow = Params.builder.get_object("miner_config_dial")

        maintext = Params.builder.get_object("maintext")
        maintext.set_text(Params.ELABEL)

        boldtext = Params.builder.get_object("boldtext")
        boldtext.set_text("ethminer.conf")

        textbuffer = Params.builder.get_object("textbuffer")
        textbuffer.set_text(Params.eparams)

        Params.builder.connect_signals(SignalEthminer())

        Params.configwindow.show_all()

    def on_xmrig_activated(self, switch, gparam):
        if switch.get_active():
            Params.xmrig = True
            self.button2.set_sensitive(True)
        else:
            Params.xmrig = False
            self.button2.set_sensitive(False)

    def on_xmrconf_clicked(self, button):
        Params.configwindow = Params.builder.get_object("miner_config_dial")

        maintext = Params.builder.get_object("maintext")
        maintext.set_text(Params.XLABEL)

        boldtext = Params.builder.get_object("boldtext")
        boldtext.set_text("config.json")

        textbuffer = Params.builder.get_object("textbuffer")
        textbuffer.set_text(Params.xparams)

        Params.builder.connect_signals(SignalXmrig())

        Params.configwindow.show_all()

    def on_button1_clicked(self, button):
        if Params.ethminer is False and Params.xmrig is False:
            Params.errortext = "There are no miners for installation!"
            dialog = DialogWindow(self)
            dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            dialog.set_resizable(False)
            dialog.run()
            dialog.destroy()
        else:
            install = InstallMinerWindow(self)
            install.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            install.set_resizable(False)
            install.show_all()


class MinerInstaller():
    Gio.Resource._register(config.res)

    window = MainWindow()
    window.set_default_size(400, 60)
    window.set_icon(
        GdkPixbuf.Pixbuf.new_from_resource(
            "/org/gtk/Femu/icons/icon.png"
        )
    )
    window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    window.set_resizable(False)
    window.connect("destroy", Gtk.main_quit)

    def run(self): MinerInstaller.window.show_all()
