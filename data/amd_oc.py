import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from threading import Thread
from os import popen as pp
from os import path
from os import system
from os import getcwd
from time import sleep

progr = 0.0
progrtext = ''
gpus = {}  #GPU IDs
amdfound = False
oldkernel = True
reboot = False
gotstats = False
selectedgpu = None

def runcmd(cmd):
	system(cmd + " >> /var/log/femu.log 2>&1")
	
class GettingStatsThread(Thread):  #install thread
	def run(self):
		global gotstats
		global GetValues
		def GetValues(i, gpu):  #Get GPU's stats function
			def GetValue(ppfile, i):  #Getting AMD GPU's IDs
				s = pp('cat /sys/class/drm/card%s/device/%s | grep "*"' % (str(i), ppfile))
				return s
			global gpus
			gpu = {'corestate' : "0", 'memstate' : "0", 'voltstate' : "0", 'coreclock' : "0", 'memclock' : "0", 'voltage' : "0", 'fan-speed' : "0", 'gpu-power' : "0", 'temp' : "0"}
			gpus.update({i : gpu})

			s = GetValue('pp_dpm_sclk', i).read()
			parts = s.rsplit(': ', 2)
			gpus[i]['coreclock'] = parts[1][:-3]
			gpus[i]['corestate'] = parts[0]

			s = GetValue('pp_dpm_mclk', i).read()
			parts = s.rsplit(': ', 2)
			gpus[i]['memclock'] = parts[1][:-3]
			gpus[i]['memstate'] = parts[0]

			sv = pp("ohgodatool -i %s --show-core | grep -A 1 'DPM state %s:' | grep VDDC" % (str(i), gpus[i]['corestate'])).read()
			sv = sv[7:]
			volt = sv.rsplit(' (', 2)
			gpus[i]['voltage'] = volt[0]
			gpus[i]['voltstate'] = volt[1][20:-2]

			s = pp("ohgodatool -i %s --show-fanspeed" % i).read()
			gpus[i]['fan-speed'] = s[:-2]

			s = pp("ohgodatool -i %s --show-temp" % i).read()
			gpus[i]['temp'] = s[:-2]

			s = pp("rocm-smi -d %s -P | grep Average" % str(i)).read()
			s = s[:-1]
			sp = s.rsplit('wer: ', 2)
			gpus[i]['gpu-power'] = sp[1]
		for i in range(13):
			if path.exists('/sys/class/drm/card%s/device/pp_dpm_sclk' % str(i)):
				GetValues(i, gpus)  #Getting stats of GPU with ID 'i' and putting it to 'gpus' dictionary
				amdfound = True
		gotstats = True
class ProgressThread(Thread):  #install thread
	def run(self):
		global progr, progrtext, oldkernel, reboot
		director = str(getcwd())  #save directory
		progr = 0.01
		
		progrtext = "Downloading ROC-smi and OhGodATool..."
		work = director + "/amd-oc-install.bash --download"
		runcmd(work)
		progr = 0.25
		
		progrtext = "Installing ROC-smi and OhGodATool..."
		work = director + "/amd-oc-install.bash --install"
		runcmd(work)
		work = 'cp amdoc /etc/init.d'
		runcmd(work)
		work = 'chmod +x /etc/init.d/amdoc'
		runcmd(work)
		work = 'update-rc.d amdoc defaults'
		runcmd(work)
		work = 'update-rc.d amdoc enable'
		runcmd(work)
		work='touch /opt/amdoverclock.bash'
		runcmd(work)
		
		progr = 0.5
		
		if oldkernel is True:
			progrtext = "Upgrading kernel with UKUU tool..."
			work = director + "/amd-oc-install.bash --kernel"
			runcmd(work)
			reboot = True
		progr = 1.0
		progrtext = "Complete"
		sleep(3)
		quit()
		
def Dialog(dialhead, dialtext, button=True):
	class DialogWindow(Gtk.Window):  #dialog window
		def __init__(self):
			Gtk.Window.__init__(self, title=dialhead)
			self.set_default_size(200, 100)
			label = Gtk.Label()
			label.set_markup("\n<big>" + dialtext + "</big>")  #window text
			box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
			box.set_homogeneous(False)
			box.pack_start(label, True, True, 0)
			if button is True:
				self.button = Gtk.Button(label="OK")
				self.button.connect("clicked", self.on_button_clicked)
				box.pack_start(self.button, True, True, 0)
			else:
				self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
				self.activity_mode = False
				GettingStatsThread().start()
			self.add(box)
			self.show_all()
		def on_button_clicked(self, button):
			self.destroy()
		def on_timeout(self, user_data):
			global gotstats
			if gotstats is True:
				self.destroy()
	dial = DialogWindow()
	dial.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
	dial.set_resizable(False)
	dial.connect("destroy", Gtk.main_quit)
	dial.show_all()
	Gtk.main()
	
class MainWindow(Gtk.Window):
	def __init__(self):
		global gpus, selectedgpu
		Gtk.Window.__init__(self, title="FEMU's AMD OC Tool (OhGodATool GUI)")
		#self.set_default_size(300, 200)
		
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		
		vbox = Gtk.Box(spacing=10)
		vbox.set_homogeneous(True)
		
		label = Gtk.Label()
		label.set_text("Select GPU:")
		vbox.pack_start(label, True, True, 0)

		gpus_store = Gtk.ListStore(int)
		for i in range(13):
			d = gpus.get(i)
			if not d == None:
				gpus_store.append([i])

		gpus_combo = Gtk.ComboBox.new_with_model(gpus_store)
		gpus_combo.connect("changed", self.on_gpus_combo_changed)
		renderer_text = Gtk.CellRendererText()
		gpus_combo.pack_start(renderer_text, True)
		gpus_combo.add_attribute(renderer_text, "text", 0)
		vbox.pack_start(gpus_combo, False, False, True)		
		
		self.button = Gtk.Button(label="Select")
		self.button.connect("clicked", self.on_gpu_clicked)
		vbox.pack_start(self.button, True, True, 0)		
		
		box.pack_start(vbox, True, True, 0)
		
		cbox = Gtk.Box(spacing=10)
		cbox.set_homogeneous(True)
		label = Gtk.Label()
		label.set_markup("<big>Core Clock</big>")
		cbox.pack_start(label, True, True, 0)
		label = Gtk.Label()
		label.set_markup("Current:")
		cbox.pack_start(label, True, True, 0)		
		self.cur_cclk = Gtk.Label()
		self.cur_cclk.set_text('0')
		cbox.pack_start(self.cur_cclk, True, True, 0)
		label = Gtk.Label()
		label.set_text("New: ")
		cbox.pack_start(label, True, True, 0)
		self.cclk = Gtk.Entry()
		cbox.pack_start(self.cclk, True, True, 0)
		self.setcclk = Gtk.Button(label="Apply")
		self.setcclk.connect("clicked", self.on_cclk_clicked)
		cbox.pack_start(self.setcclk, True, True, 0)		
		box.pack_start(cbox, True, True, 0)
		
		mbox = Gtk.Box(spacing=10)
		mbox.set_homogeneous(True)
		label = Gtk.Label()
		label.set_markup("<big>Memory Clock</big>")
		mbox.pack_start(label, True, True, 0)
		label = Gtk.Label()
		label.set_markup("Current:")
		mbox.pack_start(label, True, True, 0)
		self.cur_mclk = Gtk.Label()
		self.cur_mclk.set_text('0')
		mbox.pack_start(self.cur_mclk, True, True, 0)
		label = Gtk.Label()
		label.set_text("New: ")
		mbox.pack_start(label, True, True, 0)
		self.mclk = Gtk.Entry()
		mbox.pack_start(self.mclk, True, True, 0)
		self.setmclk = Gtk.Button(label="Apply")
		self.setmclk.connect("clicked", self.on_mclk_clicked)
		mbox.pack_start(self.setmclk, True, True, 0)		
		box.pack_start(mbox, True, True, 0)
		
		vvbox = Gtk.Box(spacing=10)
		vvbox.set_homogeneous(True)
		label = Gtk.Label()
		label.set_markup("<big>Core voltage</big>")
		vvbox.pack_start(label, True, True, 0)
		label = Gtk.Label()
		label.set_markup("Current:")
		vvbox.pack_start(label, True, True, 0)		
		self.cur_volt = Gtk.Label()
		self.cur_volt.set_text('0')
		vvbox.pack_start(self.cur_volt, True, True, 0)
		label = Gtk.Label()
		label.set_text("New: ")
		vvbox.pack_start(label, True, True, 0)
		self.volt = Gtk.Entry()
		vvbox.pack_start(self.volt, True, True, 0)
		self.setvolt = Gtk.Button(label="Apply")
		self.setvolt.connect("clicked", self.on_volt_clicked)
		vvbox.pack_start(self.setvolt, True, True, 0)		
		box.pack_start(vvbox, True, True, 0)
		
		fbox = Gtk.Box(spacing=10)
		fbox.set_homogeneous(True)
		label = Gtk.Label()
		label.set_markup("<big>Fan speed</big>")
		fbox.pack_start(label, True, True, 0)
		label = Gtk.Label()
		label.set_markup("Current:")
		fbox.pack_start(label, True, True, 0)		
		self.cur_fan = Gtk.Label()
		self.cur_fan.set_text('0')
		fbox.pack_start(self.cur_fan, True, True, 0)
		label = Gtk.Label()
		label.set_text("New: ")
		fbox.pack_start(label, True, True, 0)
		self.fan = Gtk.Entry()
		fbox.pack_start(self.fan, True, True, 0)
		self.setfan = Gtk.Button(label="Apply")
		self.setfan.connect("clicked", self.on_fan_clicked)
		fbox.pack_start(self.setfan, True, True, 0)		
		box.pack_start(fbox, True, True, 0)
		
		pbox = Gtk.Box(spacing=10)
		pbox.set_homogeneous(True)
		label = Gtk.Label()
		label.set_markup("<big>Power limit</big>")
		pbox.pack_start(label, True, True, 0)
		label = Gtk.Label()
		label.set_markup("Current Avg. Power:")
		pbox.pack_start(label, True, True, 0)
		self.cur_power = Gtk.Label()
		self.cur_power.set_text('0')
		pbox.pack_start(self.cur_power, True, True, 0)
		label = Gtk.Label()
		label.set_text("New PL: ")
		pbox.pack_start(label, True, True, 0)
		self.power = Gtk.Entry()
		pbox.pack_start(self.power, True, True, 0)
		self.setpower = Gtk.Button(label="Apply")
		self.setpower.connect("clicked", self.on_power_clicked)
		pbox.pack_start(self.setpower, True, True, 0)		
		box.pack_start(pbox, True, True, 0)
		
		sbox = Gtk.Box(spacing=10)
		sbox.set_homogeneous(True)		
		self.applyall = Gtk.Button(label="Apply all")
		self.applyall.connect("clicked", self.on_applyall_clicked)
		sbox.pack_start(self.applyall, True, True, 0)
		self.write = Gtk.Button(label="Write this settings to an autostart script")
		self.write.connect("clicked", self.on_write_clicked)
		sbox.pack_start(self.write, True, True, 0)		
		box.pack_start(sbox, True, True, 0)		
		
		self.add(box)	
		self.show_all()
	def on_applyall_clicked(self, button):
		global gpus, selectedgpu
		if self.power.get_text().isdigit() and self.cclk.get_text().isdigit() and self.mclk.get_text().isdigit() and self.fan.get_text().isdigit() and self.volt.get_text().isdigit() and not selectedgpu == None:
			cmd = "ohgodatool -i %s --core-state %s --core-clock %s" % (str(selectedgpu), gpus[selectedgpu]['corestate'], self.cclk.get_text())
			output = pp(cmd).read()
			print(cmd)
			sleep(2)
			cmd = "ohgodatool -i %s --mem-state %s --mem-clock %s" % (str(selectedgpu), gpus[selectedgpu]['memstate'], self.mclk.get_text())
			output = output + "\n" + pp(cmd).read()
			print(cmd)
			sleep(2)
			cmd = "ohgodatool -i %s --volt-state %s --vddc-table-set %s" % (str(selectedgpu), gpus[selectedgpu]['voltstate'], self.volt.get_text())
			output = output + "\n" + pp(cmd).read()
			print(cmd)
			sleep(2)			
			cmd = "ohgodatool -i %s --set-fanspeed %s" % (str(selectedgpu), self.fan.get_text())
			output = output + "\n" + pp(cmd).read()
			print(cmd)
			sleep(2)
			cmd = "ohgodatool -i %s --set-max-power %s" % (str(selectedgpu), self.power.get_text())
			output = output + "\n" + pp(cmd).read()
			print(cmd)
			sleep(2)			
			Dialog("Info", "Result:\n<small>" + output + "</small>")
		else:
			Dialog("Error!", "Input data is incorrect or GPU is not selected!")
	def on_write_clicked(self, button):
		global gpus, selectedgpu
		if self.power.get_text().isdigit() and self.cclk.get_text().isdigit() and self.mclk.get_text().isdigit() and self.fan.get_text().isdigit() and self.volt.get_text().isdigit() and not selectedgpu == None:
			work = "bash amd-oc-install.bash --cleargpu " + str(selectedgpu)
			runcmd(work)
			work = "echo 'ohgodatool -i %s --core-state %s --core-clock %s #GPU%s' >> /opt/amdoverclock.bash" % (str(selectedgpu), gpus[selectedgpu]['corestate'], self.cclk.get_text(), str(selectedgpu))
			runcmd(work)
			work = "echo 'ohgodatool -i %s --mem-state %s --mem-clock %s #GPU%s' >> /opt/amdoverclock.bash" % (str(selectedgpu), gpus[selectedgpu]['memstate'], self.mclk.get_text(), str(selectedgpu))
			runcmd(work)
			work = "echo 'ohgodatool -i %s --set-fanspeed %s #GPU%s' >> /opt/amdoverclock.bash" % (str(selectedgpu), self.fan.get_text(), str(selectedgpu))
			runcmd(work)
			work = "echo 'ohgodatool -i %s --set-max-power %s #GPU%s' >> /opt/amdoverclock.bash" % (str(selectedgpu), self.power.get_text(), str(selectedgpu))
			runcmd(work)
			work = "echo 'ohgodatool -i %s --volt-state %s --vddc-table-set %s #GPU%s' >> /opt/amdoverclock.bash" % (str(selectedgpu), gpus[selectedgpu]['voltstate'], self.volt.get_text(), str(selectedgpu))
			runcmd(work)
			Dialog("OK", "This settings for GPU %s are on autostart now." % str(selectedgpu))
		else:
			Dialog("Error!", "Input data is incorrect or GPU is not selected!")
	def on_cclk_clicked(self, button):
		global gpus, selectedgpu
		if self.cclk.get_text().isdigit() and not selectedgpu == None:
			cmd = "ohgodatool -i %s --core-state %s --core-clock %s" % (str(selectedgpu), gpus[selectedgpu]['corestate'], self.cclk.get_text())
			output = pp(cmd).read()
			print(cmd)
			sleep(2)
			Dialog("Info", "Result:\n<small>" + output + "</small>")
			GetValues(selectedgpu, gpus)
			self.cur_cclk.set_text(gpus[selectedgpu]['coreclock'])
			self.cur_mclk.set_text(gpus[selectedgpu]['memclock'])
			self.cur_volt.set_text(gpus[selectedgpu]['voltage'])
			self.cur_fan.set_text(gpus[selectedgpu]['fan-speed'])
			self.cur_power.set_text(gpus[selectedgpu]['gpu-power'])			
		else:
			Dialog("Error!", "Input data is incorrect or GPU is not selected!")
	def on_mclk_clicked(self, button):
		global gpus, selectedgpu
		if self.mclk.get_text().isdigit() and not selectedgpu == None:
			cmd = "ohgodatool -i %s --mem-state %s --mem-clock %s" % (str(selectedgpu), gpus[selectedgpu]['memstate'], self.mclk.get_text())
			output = pp(cmd).read()
			print(cmd)
			sleep(2)
			Dialog("Info", "Result:\n<small>" + output + "</small>")
			GetValues(selectedgpu, gpus)
			self.cur_cclk.set_text(gpus[selectedgpu]['coreclock'])
			self.cur_mclk.set_text(gpus[selectedgpu]['memclock'])
			self.cur_volt.set_text(gpus[selectedgpu]['voltage'])
			self.cur_fan.set_text(gpus[selectedgpu]['fan-speed'])
			self.cur_power.set_text(gpus[selectedgpu]['gpu-power'])	
		else:
			Dialog("Error!", "Input data is incorrect or GPU is not selected!")	
	def on_volt_clicked(self, button):
		global gpus, selectedgpu
		if self.volt.get_text().isdigit() and not selectedgpu == None:
			cmd = "ohgodatool -i %s --volt-state %s --vddc-table-set %s" % (str(selectedgpu), gpus[selectedgpu]['voltstate'], self.volt.get_text())
			output = pp(cmd).read()
			print(cmd)
			sleep(2)
			Dialog("Info", "Result:\n<small>" + output + "</small>")
			GetValues(selectedgpu, gpus)
			self.cur_cclk.set_text(gpus[selectedgpu]['coreclock'])
			self.cur_mclk.set_text(gpus[selectedgpu]['memclock'])
			self.cur_volt.set_text(gpus[selectedgpu]['voltage'])
			self.cur_fan.set_text(gpus[selectedgpu]['fan-speed'])
			self.cur_power.set_text(gpus[selectedgpu]['gpu-power'])	
		else:
			Dialog("Error!", "Input data is incorrect or GPU is not selected!")
	def on_fan_clicked(self, button):
		global gpus, selectedgpu
		if self.fan.get_text().isdigit() and not selectedgpu == None:
			cmd = "ohgodatool -i %s --set-fanspeed %s" % (str(selectedgpu), self.fan.get_text())
			output = pp(cmd).read()
			print(cmd)
			sleep(2)
			Dialog("Info", "Result:\n<small>" + output + "</small>")
			GetValues(selectedgpu, gpus)
			self.cur_cclk.set_text(gpus[selectedgpu]['coreclock'])
			self.cur_mclk.set_text(gpus[selectedgpu]['memclock'])
			self.cur_volt.set_text(gpus[selectedgpu]['voltage'])
			self.cur_fan.set_text(gpus[selectedgpu]['fan-speed'])
			self.cur_power.set_text(gpus[selectedgpu]['gpu-power'])	
		else:
			Dialog("Error!", "Input data is incorrect or GPU is not selected!")
	def on_power_clicked(self, button):
		global gpus, selectedgpu
		if self.power.get_text().isdigit() and not selectedgpu == None:
			cmd = "ohgodatool -i %s --set-max-power %s" % (str(selectedgpu), self.power.get_text())
			output = pp(cmd).read()
			print(cmd)
			sleep(2)
			Dialog("Info", "Result:\n<small>" + output + "</small>")
			GetValues(selectedgpu, gpus)
			self.cur_cclk.set_text(gpus[selectedgpu]['coreclock'])
			self.cur_mclk.set_text(gpus[selectedgpu]['memclock'])
			self.cur_volt.set_text(gpus[selectedgpu]['voltage'])
			self.cur_fan.set_text(gpus[selectedgpu]['fan-speed'])
			self.cur_power.set_text(gpus[selectedgpu]['gpu-power'])
		else:
			Dialog("Error!", "Input data is incorrect or GPU is not selected!")
	def on_gpus_combo_changed(self, combo):
		global selectedgpu
		tree_iter = combo.get_active_iter()
		if tree_iter is not None:
			model = combo.get_model()
			selectedgpu = model[tree_iter][0]
	def on_gpu_clicked(self, button):
		global selectedgpu, gpus
		if not selectedgpu == None:
				self.cur_cclk.set_text(gpus[selectedgpu]['coreclock'])
				self.cur_mclk.set_text(gpus[selectedgpu]['memclock'])
				self.cur_volt.set_text(gpus[selectedgpu]['voltage'])
				self.cur_fan.set_text(gpus[selectedgpu]['fan-speed'])
				self.cur_power.set_text(gpus[selectedgpu]['gpu-power'])
class InstallWindow(Gtk.Window):
	def __init__(self):
		global oldkernel
		Gtk.Window.__init__(self, title="Upgrading system for AMD OC")
		self.set_default_size(500, 150)
		label = Gtk.Label()
		if oldkernel is True:
			label.set_markup("<big>Hello!</big>\n"
							"Your Linux kernel version is: " + pp("uname -r").read() + ""
							"It will be upgraded to version 4.17 because there are some OC problems\n"
							"on older kernels with AMD. Overclocking software will be installed too."
							)  #window text
		else:
			label.set_markup("<big>Hello!</big>\n"
							"Your Linux kernel version is: " + pp("uname -r").read() + ""
							"Only overclocking software will be installed."
							)  #window text
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		box.pack_start(label, True, True, 0)
		
		self.button = Gtk.Button(label="Install")
		self.button.connect("clicked", self.on_button_clicked)

		self.progressbar = Gtk.ProgressBar()
		self.progressbar.set_show_text(True)
		
		box.pack_start(self.progressbar, True, True, 0)
		box.pack_start(self.button, True, True, 0)

		self.add(box)
		
		self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
		self.activity_mode = False
		
		self.show_all()
	def on_button_clicked(self, button):
		self.button.set_sensitive(False)
		ProgressThread().start()
	def on_timeout(self, user_data):
		global progr, progrtext
		self.progressbar.set_fraction(progr)
		self.progressbar.set_text(progrtext)
		if reboot == True:
			Dialog("Reboot", "Press OK to reboot.")
			pp("/sbin/reboot")
			quit()
		return True

Dialog("FEMU", "Getting GPU stats...", False)

if amdfound is False:
	Dialog("Error!", "AMD GPU not found!")
	quit()

if not '4.17' in pp("uname -r").read():
	install = InstallWindow()
	install.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
	install.set_resizable(False)
	install.connect("destroy", Gtk.main_quit)
	install.show_all()
	Gtk.main()
elif '4.17' in pp("uname -r").read() and not path.exists('/usr/src/OhGodATool') or not path.exists('/usr/src/ROC-smi'):
	oldkernel = False
	install = InstallWindow()
	install.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
	install.set_resizable(False)
	install.connect("destroy", Gtk.main_quit)
	install.show_all()
	Gtk.main()	
else:
	print("test")
	window = MainWindow()
	window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
	window.set_resizable(False)
	window.connect("destroy", Gtk.main_quit)
	window.show_all()
	Gtk.main()	
