#!/usr/bin/env python3

'''
 FEMU - Free & Easy Mining on Ubuntu

 Nvidia GPU overclocking tool
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
import json
import gi

from gi.repository import Gtk, Gio, GdkPixbuf
from os import popen as pp
from os import path
from .femu_config import config


def GetParam(gpu, param):  # gets GPU's params
    def get(param):
        return int(pp('nvidia-settings -q "' + param + '" -t').read())

    if param is "fan":
        return get('[fan:%s]/GPUTargetFanSpeed' % gpu)
    if param is "coreclock":
        return get('[gpu:%s]/GPUGraphicsClockOffset' % gpu)
    if param is "memclock":
        return get('[gpu:%s]/GPUMemoryTransferRateOffset' % gpu)
    if param is "pl":
        return float(
                    pp(
                        "nvidia-smi --id=%s --query-gpu=power.limit --format=csv,noheader,nounits" % gpu
                    ).read())


def SetParam(gpu, param, val):  # changes GPU's params
    def apply(param):
        return pp('nvidia-settings -a "' + param + '"').read()

    if param is "fan":
        result = apply('[gpu:%s]/GPUFanControlState=1' % gpu)
        result += apply('[fan:%s]/GPUTargetFanSpeed=%s' % (gpu, val))
        return result
    if param is "coreclock":
        result = apply('[gpu:%s]/GPUGraphicsClockOffset[2]=%s' % (gpu, val))
        result += apply('[gpu:%s]/GPUGraphicsClockOffset[3]=%s' % (gpu, val))
        return result
    if param is "memclock":
        result = apply(
                      '[gpu:%s]/GPUMemoryTransferRateOffset[2]=%s' % (
                                                                     gpu, val))
        result += apply(
                       '[gpu:%s]/GPUMemoryTransferRateOffset[3]=%s' % (
                                                                      gpu, val)
                  )
        return result
    if param is "pl":
        result = pp('nvidia-smi --id=%s --power-limit=%s' % (gpu, val)).read()
        return result
    if param is "other":
        result = apply(val)
        return(result)


class Signal():  # signal handler for all windows
    def on_coreclock_clicked(self, button):
        if self.CheckSelection():
            entry = NvidiaOC.builder.get_object("coreclock_entry")

            try:
                NvidiaOC.gpus[NvidiaOC.gpu]["coreclock"] = int(
                                                           entry.get_text()
                                                           )
            except ValueError:
                NvidiaOC.info_label.set_text("Incorrect value!")
                NvidiaOC.dialog.show()
                return -1

            coreclock = NvidiaOC.builder.get_object("coreclock_val")
            coreclock.set_text(str(
                NvidiaOC.gpus[int(
                    NvidiaOC.gpu)]["coreclock"]) + " Mhz"
            )
            result = SetParam(NvidiaOC.gpu, "coreclock", entry.get_text())

            NvidiaOC.info_label.set_text(
                "Result: %s\nIf empty then all's OK" % result
            )
            NvidiaOC.dialog.set_title("Operation result")
            NvidiaOC.dialog.show()

    def on_memclock_clicked(self, button):
        if self.CheckSelection():
            entry = NvidiaOC.builder.get_object("memclock_entry")

            try:
                NvidiaOC.gpus[NvidiaOC.gpu]["memclock"] = int(entry.get_text())
            except ValueError:
                NvidiaOC.info_label.set_text("Incorrect value!")
                NvidiaOC.dialog.show()
                return -1

            memclock = NvidiaOC.builder.get_object("memclock_val")
            memclock.set_text(str(
                NvidiaOC.gpus[NvidiaOC.gpu]["memclock"]) + " Mhz"
            )
            result = SetParam(NvidiaOC.gpu, "memclock", entry.get_text())

            NvidiaOC.info_label.set_text(
                "Result: %s\nIf empty then all's OK" % result
            )
            NvidiaOC.dialog.set_title("Operation result")
            NvidiaOC.dialog.show()

    def on_pl_clicked(self, button):
        if self.CheckSelection():
            entry = NvidiaOC.builder.get_object("pl_entry")

            try:
                NvidiaOC.gpus[NvidiaOC.gpu]["powerlimit"] = float(
                    entry.get_text())
            except ValueError:
                NvidiaOC.info_label.set_text("Incorrect value!")
                NvidiaOC.dialog.show()
                return -1

            pl = NvidiaOC.builder.get_object("pl_val")
            pl.set_text(str(NvidiaOC.gpus[NvidiaOC.gpu]["powerlimit"]) + " W")
            result = SetParam(NvidiaOC.gpu, "pl", entry.get_text())

            NvidiaOC.info_label.set_text(
                "Result: %s\nIf empty then all's OK" % result
            )
            NvidiaOC.dialog.set_title("Operation result")
            NvidiaOC.dialog.show()

    def on_fan_clicked(self, button):
        if self.CheckSelection():
            entry = NvidiaOC.builder.get_object("fan_entry")

            try:
                NvidiaOC.gpus[NvidiaOC.gpu]["fanspeed"] = int(entry.get_text())
            except ValueError:
                NvidiaOC.info_label.set_text("Incorrect value!")
                NvidiaOC.dialog.show()
                return -1

            fanspeed = NvidiaOC.builder.get_object("fan_val")
            fanspeed.set_text(str(
                NvidiaOC.gpus[NvidiaOC.gpu]["fanspeed"]) + " %"
            )
            result = SetParam(NvidiaOC.gpu, "fan", entry.get_text())

            NvidiaOC.info_label.set_text(
                "Result: %s\nIf empty then all's OK" % result
            )
            NvidiaOC.dialog.set_title("Operation result")
            NvidiaOC.dialog.show()

    def on_applyall_clicked(self, button):
        fan_entry = NvidiaOC.builder.get_object("fan_entry").get_text()
        coreclock_entry = NvidiaOC.builder.get_object(
            "coreclock_entry").get_text()
        memclock_entry = NvidiaOC.builder.get_object(
            "memclock_entry").get_text()
        pl_entry = NvidiaOC.builder.get_object(
            "pl_entry").get_text()

        try:
            NvidiaOC.gpus[NvidiaOC.gpu]["fanspeed"] = int(fan_entry)
            NvidiaOC.gpus[NvidiaOC.gpu]["coreclock"] = int(coreclock_entry)
            NvidiaOC.gpus[NvidiaOC.gpu]["memclock"] = int(memclock_entry)
            NvidiaOC.gpus[NvidiaOC.gpu]["powerlimit"] = int(pl_entry)
        except ValueError:
            NvidiaOC.info_label.set_text("Incorrect value!")
            NvidiaOC.dialog.show()
            return -1

        coreclock = NvidiaOC.builder.get_object("coreclock_val")
        memclock = NvidiaOC.builder.get_object("memclock_val")
        pl = NvidiaOC.builder.get_object("pl_val")
        fanspeed = NvidiaOC.builder.get_object("fan_val")

        coreclock.set_text(str(
            NvidiaOC.gpus[NvidiaOC.gpu]["coreclock"]) + " Mhz")
        memclock.set_text(str(
            NvidiaOC.gpus[NvidiaOC.gpu]["memclock"]) + " Mhz")
        pl.set_text(str(
            NvidiaOC.gpus[NvidiaOC.gpu]["powerlimit"]) + " W")
        fanspeed.set_text(str(
            NvidiaOC.gpus[NvidiaOC.gpu]["fanspeed"]) + " %")

        result = SetParam(NvidiaOC.gpu, "fan", int(fan_entry))
        result += SetParam(NvidiaOC.gpu, "memclock", int(memclock_entry))
        result += SetParam(NvidiaOC.gpu, "coreclock", int(coreclock_entry))
        result += SetParam(NvidiaOC.gpu, "pl", int(pl_entry))

        NvidiaOC.info_label.set_text(
            "Result: %s\nIf empty then all's OK" % result
        )
        NvidiaOC.dialog.set_title("Operation result")
        NvidiaOC.dialog.show()

    def on_saveall_clicked(self, button):
        with open('/etc/miners/nvidia_oc.json') as json_data:
            gpusjson = json.load(json_data)
        gpusjson = {**gpusjson, **NvidiaOC.gpus}

        with open('/etc/miners/nvidia_oc.json', 'w') as outfile:
            json.dump(gpusjson, outfile)

    def on_edit_other_clicked(self, button):
        NvidiaOC.others_window.show()

    def on_gpu_changed(self, button):
        gpu = NvidiaOC.gpu_selector.get_active_text()[-1:]
        if gpu.isdigit():
            NvidiaOC.gpu = gpu
        else:
            NvidiaOC.gpu = None
            return -1

        fan_entry = NvidiaOC.builder.get_object("fan_entry")
        coreclock_entry = NvidiaOC.builder.get_object("coreclock_entry")
        memclock_entry = NvidiaOC.builder.get_object("memclock_entry")
        pl_entry = NvidiaOC.builder.get_object("pl_entry")

        coreclock = NvidiaOC.builder.get_object("coreclock_val")
        memclock = NvidiaOC.builder.get_object("memclock_val")
        pl = NvidiaOC.builder.get_object("pl_val")
        fanspeed = NvidiaOC.builder.get_object("fan_val")

        coreclock_entry.set_text("0")
        memclock_entry.set_text("0")
        pl_entry.set_text(str(NvidiaOC.gpus[NvidiaOC.gpu]["powerlimit"]))
        fan_entry.set_text(str(NvidiaOC.gpus[NvidiaOC.gpu]["fanspeed"]))

        coreclock.set_text(str(
            NvidiaOC.gpus[NvidiaOC.gpu]["coreclock"]) + " Mhz")
        memclock.set_text(str(
            NvidiaOC.gpus[NvidiaOC.gpu]["memclock"]) + " Mhz")
        pl.set_text(str(
            NvidiaOC.gpus[NvidiaOC.gpu]["powerlimit"]) + " W")
        fanspeed.set_text(str(
            NvidiaOC.gpus[NvidiaOC.gpu]["fanspeed"]) + " %")

    def on_save_other_clicked(self, button):
        NvidiaOC.gpus[NvidiaOC.gpu].update({entry : 1})

        with open('/etc/miners/nvidia_oc.json') as json_data:
            gpusjson = json.load(json_data)
        gpusjson = {**gpusjson, **NvidiaOC.gpus}

        with open('/etc/miners/nvidia_oc.json', 'w') as outfile:
            json.dump(gpusjson, outfile)

    def on_apply_other_clicked(self, button):
        entry = NvidiaOC.builder.get_object("other_entry").get_text()
        result = SetParam(None, "other", entry)

        NvidiaOC.info_label.set_text(
            "Result: %s\nIf empty then all's OK" % result
        )
        NvidiaOC.dialog.set_title("Operation result")
        NvidiaOC.dialog.show()

    def on_dialog_close_clicked(self, button):
        NvidiaOC.dialog.hide()

    def on_edit_oc_clicked(self, button):
        pp("leafpad /etc/miners/nvidia_oc.json")

    def CheckSelection(self):
        if NvidiaOC.gpu not in NvidiaOC.gpus:
            NvidiaOC.info_label.set_text("Please select GPU!")
            NvidiaOC.dialog.show()
            return False
        else:
            return True


class NvidiaOC():
    Gio.Resource._register(config.res)

    builder = Gtk.Builder.new_from_resource(
        "/org/gtk/Femu/glade/nvidia_oc_config.glade")
    dialogbuilder = Gtk.Builder.new_from_resource(
        "/org/gtk/Femu/glade/dialog.glade")

    mainwindow = builder.get_object("window")
    mainwindow.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    mainwindow.set_icon(
        GdkPixbuf.Pixbuf.new_from_resource(
            "/org/gtk/Femu/icons/icon.png"
        )
    )

    gpu_selector = builder.get_object("gpu_selector")

    gpu = None
    gpus = {}
    count = int(
        pp(
            "nvidia-smi --id=0 --query-gpu=count --format=csv,noheader"
        ).read())
    for i in range(0, count):
        gpus[str(i)] = {
                        "fanspeed": GetParam(i, "fan"),
                        "powerlimit": GetParam(i, "pl"),
                        "coreclock": GetParam(i, "coreclock"),
                        "memclock": GetParam(i, "memclock")
                        }

    for i in gpus:
        gpu_selector.append_text("GPU " + i)

    dialog = dialogbuilder.get_object("dialog")
    dialog.set_transient_for(mainwindow)
    info_label = dialogbuilder.get_object("info_label")

    others_window = builder.get_object("others_window")
    others_window.set_transient_for(mainwindow)

    builder.connect_signals(Signal())
    dialogbuilder.connect_signals(Signal())

    def run(self): NvidiaOC.mainwindow.show_all()
