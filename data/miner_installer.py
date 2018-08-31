import gi, os, time
from threading import Thread
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# variables for Ethminer parameters
nvidia = False
amd = True
devfeeoff = False
ethminer = False
ethminerssl = False
ethminerbuild = False
ewallet = ""
epool1 = ""
stratumtype = "stratum"
# variables for XMRig-AMD parameters
xmrig = False
xwallet = ""
xpool1 = ""
algo = ""

user = "" # variable for the user for whom tool are installing software
errortext = "" # variable for error text for dialog
errorhead = "Error!" # variable for header for dialog
progr = 0.0 # variable for progressbar percentage
progrtext = "" # variable for progressbar text
dialrun = False # variable for dialog running

def runcmd(cmd):
	os.system(cmd + " >> /var/log/femu.log 2>&1")

class ProgressThread(Thread): # class for scripts running
	def run(self):
		# all global variables
		global progr, progrtext, desktop, stratumtype, ethminerssl, ewallet, epool1, amd, nvidia, user, ethminerbuild, algo, xwallet, xpool1, devfeeoff, errorhead, errortext, dialrun
		director = str(os.getcwd()) # save directory
		progr = 0.01 # progress to 1%
		progrtext = "Loading" # установка текста прогрессбара
		work = director + "/miner-install.bash --step1 " + desktop 
		runcmd(work) # launching script with directory
		progrtext = "Unpacking"
		progr = 0.05
		progrtext = "Running the install script"
		if ethminer == True: # if Ethminer activated
			if ethminerssl == True: # connection type
				ssl = "ssl"
			else:
				ssl = "tcp"
			if ethminerbuild == True: # running script for optimized build 
				work = director + "/miner-install.bash --ethminer-build " + desktop + "/miners"
				runcmd(work)
				progr = 0.5
				progrtext = "Building target Ethminer"
				work = director + "/miner-install.bash --ethminer-build2 " + desktop + "/miners"
				runcmd(work)
				progr = 0.99
			else: # default download a release from GitHub
				work = director + "/miner-install.bash --ethminer-bin " + desktop + "/miners"
				runcmd(work)
				progr = 0.99
			# making a file for start script
			work = director + "/miner-install.bash --step2 " + desktop + "/ethminer.bash"
			runcmd(work)
			# determining the type of graphics cards for Ethminer
			if nvidia == True and amd == False:
				mode = "-U"
			if nvidia == True and amd == True:
				mode = "-X"
			if nvidia == False and amd == True:
				mode = "-G"
			# making start script
			work = "echo '#!/bin/bash' > %s" % desktop + "/ethminer.bash"
			runcmd(work)
			work = "echo '%s/miners/ethminer/build/ethminer/ethminer --farm-recheck 200 --tstart 45 %s -P %s+%s://%s@%s' >> %s" % (desktop, mode, stratumtype, ssl, ewallet, epool1, desktop + "/ethminer.bash")
			runcmd(work)
			
			with open ('ethminer', 'r') as f:
				old_data = f.read()
			new_data = old_data.replace('$APPLICATION_PATH=""', '$APPLICATION_PATH="' + desktop + '"')
			with open ('ethminer', 'w') as f:
				f.write(new_data)
			
			work = 'cp ethminer /etc/init.d'
			runcmd(work)
			work = 'chmod +x /etc/init.d/ethminer'
			runcmd(work)
			work = 'update-rc.d ethminer defaults'
			runcmd(work)
			work = 'update-rc.d ethminer enable'
			runcmd(work)
			
			progr = 1.0

		if xmrig == True: # if XMRig-AMD activated
			progr = 0.01
			progrtext = "Installing dependencies and system updates"
			work = director + "/miner-install.bash --step1xmr " + desktop + "/miners"
			runcmd(work)
			progr = 0.1
			progrtext = "XMRig miner downloading"
			work = director + "/miner-install.bash --step2xmr " + desktop + "/miners"
			runcmd(work)
			progr = 0.15
			if devfeeoff == True: # devfee off
				progrtext = "Devfee off"
				work = director + "/miner-install.bash --devfeeoff " + desktop + "/miners"
				runcmd(work)
				progr = 0.16
			progrtext = "Preparating XMRig build"
			work = director + "/miner-install.bash --step3xmr " + desktop + "/miners"
			runcmd(work)
			progr = 0.3
			progrtext = "Build target XMRig"
			work = director + "/miner-install.bash --step4xmr " + desktop
			runcmd(work)
			progr = 0.97
			progrtext = "Сonfiguring XMRig"
			work = "echo '#!/bin/bash' > %s" % desktop + "/xmrig-amd.bash" # making start script
			runcmd(work)
			if devfeeoff == True:
				work = "echo '%s/miners/xmrig-amd/xmrig-amd%s -l xmrig.log --donate-level 0 --api-port 4444 -o %s -u %s -p x --variant 1 -k' >> %s" % (desktop, algo, xpool1, xwallet, desktop + "/xmrig-amd.bash")
			else:
				work = "echo '%s/miners/xmrig-amd/xmrig-amd%s -l xmrig.log --donate-level 1 --api-port 4444 -o %s -u %s -p x --variant 1 -k' >> %s" % (desktop, algo, xpool1, xwallet, desktop + "/xmrig-amd.bash")
			runcmd(work)
			work = "chmod 777 " + desktop + "/xmrig-amd.bash"
			runcmd(work)
			work = "chmod ugo+x " + desktop + "/xmrig-amd.bash"
			runcmd(work)
			
			with open ('xmrig', 'r') as f:
				old_data = f.read()
			new_data = old_data.replace('$APPLICATION_PATH=""', '$APPLICATION_PATH="' + desktop + '"')
			with open ('xmrig', 'w') as f:
				f.write(new_data)
			
			work = 'cp xmrig /etc/init.d'
			runcmd(work)
			work = 'chmod +x /etc/init.d/xmrig'
			runcmd(work)
			work = 'update-rc.d xmrig defaults'
			runcmd(work)
			work = 'update-rc.d xmrig enable'
			runcmd(work)			
			
			progr = 1.0
		# dialog for finish installation
		errorhead = "Success!"
		errortext = "Software for mining has been installed.\nAll miners were added to autostart script.\nTo see your hashrate run: sudo screen -r (miner)\nGood luck!\nPress 'OK' to quit."
		dialrun = True
class EthminerConfigWindow(Gtk.Window): # Ethminer configuration window
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="Ethminer Configuration")
		global ewallet, epool1, stratumtype, ethminerbuild

		self.set_border_width(10)
		self.set_default_size(300, 250)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		label = Gtk.Label()
		label.set_markup("What's your videocards manufacturer?")
		box.pack_start(label, True, True, 0)

		vbox = Gtk.Box(spacing=6)
		vbox.set_homogeneous(False)
		box.pack_start(vbox, True, True, 0)

		label = Gtk.Label()
		label.set_markup("<big>Nvidia</big>")
		vbox.pack_start(label, True, True, 0)

		self.nvswitch = Gtk.Switch()
		self.nvswitch.connect("notify::active", self.on_nvidia_activated)
		if nvidia == True: 
			self.nvswitch.set_active(True)
		else:
			self.nvswitch.set_active(False)
		vbox.pack_start(self.nvswitch, True, True, 0)

		label = Gtk.Label()
		label.set_markup("<big>AMD</big>")
		vbox.pack_start(label, True, True, 0)

		self.amdswitch = Gtk.Switch()
		self.amdswitch.connect("notify::active", self.on_amd_activated)
		if amd == True:
			self.amdswitch.set_active(True)
		else:
			self.amdswitch.set_active(False)
		vbox.pack_start(self.amdswitch, True, True, 0)

		hbox = Gtk.Box(spacing=6)
		hbox.set_homogeneous(False)
		box.pack_start(hbox, True, True, 0)

		label = Gtk.Label()
		label.set_text("Use build from sources with newest\n"
				"compilers, rebuild Ethash cores for\n"
				"AMD. This gives a hashrate increase\n"
				"Enable, if you don't mind the time!")
		hbox.pack_start(label, True, True, 0)

		self.buildswitch = Gtk.Switch()
		self.buildswitch.connect("notify::active", self.on_build_activated)
		if ethminerbuild == True:
			self.buildswitch.set_active(True)
		else:
			self.buildswitch.set_active(False)
		if nvidia == True:
			self.buildswitch.set_sensitive(False)
		hbox.pack_start(self.buildswitch, True, True, 0)

		label = Gtk.Label()
		label.set_text("Pool:")
		box.pack_start(label, True, True, 0)

		self.epool = Gtk.Entry()
		if epool1 == "":
			self.epool.set_text("example.com:1234")
		else:
			self.epool.set_text(epool1)
		box.pack_start(self.epool, True, True, 0)
		label = Gtk.Label()
		label.set_text("Wallet (pool login):")
		box.pack_start(label, True, True, 0)

		self.ewal = Gtk.Entry()
		box.pack_start(self.ewal, True, True, 0)
		if ewallet == "":
			self.ewal.set_text("0x1245...")
		else:
			self.ewal.set_text(ewallet)

		label = Gtk.Label()
		label.set_text("Stratum type:")
		box.pack_start(label, True, True, 0)

		hbox = Gtk.Box(spacing=6)
		hbox.set_homogeneous(False)
		box.pack_start(hbox, True, True, 0)

		stratum = Gtk.RadioButton.new_with_label_from_widget(None, "stratum")
		stratum.connect("toggled", self.on_stratum_toggled, "stratum")
		hbox.pack_start(stratum, False, False, 0)
		if stratumtype == "stratum":
			stratum.set_active(True)
		else:
			stratum.set_active(False)

		stratum1 = Gtk.RadioButton.new_from_widget(stratum)
		stratum1.set_label("stratum1")
		stratum1.connect("toggled", self.on_stratum_toggled, "stratum1")
		hbox.pack_start(stratum1, False, False, 0)
		if stratumtype == "stratum1":
			stratum1.set_active(True)

		stratum2 = Gtk.RadioButton.new_with_mnemonic_from_widget(stratum,
		"stratum2")
		stratum2.connect("toggled", self.on_stratum_toggled, "stratum2")
		hbox.pack_start(stratum2, False, False, 0)
		if stratumtype == "stratum2":
			stratum2.set_active(True)

		wbox = Gtk.Box(spacing=6)
		wbox.set_homogeneous(False)
		box.pack_start(wbox, True, True, 0)

		label = Gtk.Label()
		label.set_text("           SSL:           ")
		wbox.pack_start(label, True, True, 0)

		self.sslswitch = Gtk.Switch()
		self.sslswitch.connect("notify::active", self.on_ssl_activated)
		if ethminerssl == True:
			self.sslswitch.set_active(True)
		else:
			self.sslswitch.set_active(False)
		wbox.pack_start(self.sslswitch, True, True, 0)

		self.button = Gtk.Button(label="Apply")
		self.button.connect("clicked", self.on_button_clicked)
		box.pack_start(self.button, True, True, 0)

		self.add(box)
	def on_button_clicked(self, button): # if button clicked, then save settings and close the window
		global ewallet, epool1
		ewallet = self.ewal.get_text()	
		epool1 = self.epool.get_text()
		self.destroy()
	def on_nvidia_activated(self, switch, gparam):
		global nvidia, amd
		if switch.get_active():
			nvidia = True
			self.buildswitch.set_active(False) # disabling Ethminer building for Nvidia
			self.buildswitch.set_sensitive(False)
			ethminerbuild = False
		else:
			if not self.amdswitch.get_active():
				self.amdswitch.set_active(True)
				amd = True
			nvidia = False
			self.buildswitch.set_sensitive(True)
	def on_amd_activated(self, switch, gparam):
		global nvidia, amd
		if switch.get_active():
			amd = True
		else: 
			if not self.nvswitch.get_active():
				self.nvswitch.set_active(True)
				nvidia = True
			amd = False
	def on_build_activated(self, switch, gparam):
		global ethminerbuild 
		if switch.get_active():
			ethminerbuild = True
		else:
			ethminerbuild = False
	def on_stratum_toggled(self, button, name):
		global stratumtype 
		if button.get_active():
			stratumtype = name
	def on_ssl_activated(self, switch, gparam):
		global ethminerssl 
		if switch.get_active():
			ethminerssl = True
		else:
			ethminerssl = False
		
class XmrigConfigWindow(Gtk.Window): # XMRig-AMD configuring window
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="XMRig-AMD Configuration")
		global xwallet, xpool1, devfeeoff, algo
		self.set_border_width(10)

		self.set_default_size(300, 250)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		label = Gtk.Label()
		label.set_markup("It can be installed only for AMD GPUs\nIf you haven't installed AMD driver, XMRig installation will be failed!")
		box.pack_start(label, True, True, 0)


		hbox = Gtk.Box(spacing=6)
		hbox.set_homogeneous(False)
		box.pack_start(hbox, True, True, 0)

		label = Gtk.Label()
		label.set_text("Disable devfee (XMRig developer\nwould like to if removing the devfee, then making a donation\n XMR and BTC adresses you can see on GitHub,\njust search 'xmrig-amd'")
		hbox.pack_start(label, True, True, 0)

		self.devfeeswitch = Gtk.Switch()
		self.devfeeswitch.connect("notify::active", self.on_devfeeoff_activated)
		if devfeeoff == True:
			self.devfeeswitch.set_active(True)
		else:
			self.devfeeswitch.set_active(False)
		hbox.pack_start(self.devfeeswitch, True, True, 0)

		label = Gtk.Label()
		label.set_text("Pool:")
		box.pack_start(label, True, True, 0)

		self.xpool = Gtk.Entry()
		if xpool1 == "":
			self.xpool.set_text("example.com:1234")
		else:
			self.xpool.set_text(xpool1)
		box.pack_start(self.xpool, True, True, 0)

		label = Gtk.Label()
		label.set_text("Wallet (pool login):")
		box.pack_start(label, True, True, 0)

		self.xwal = Gtk.Entry()
		box.pack_start(self.xwal, True, True, 0)
		if xwallet == "":
			self.xwal.set_text("4abcd...")
		else:
			self.xwal.set_text(xwallet)

		label = Gtk.Label()
		label.set_text("Algo:")
		box.pack_start(label, True, True, 0)

		hbox = Gtk.Box(spacing=6)
		hbox.set_homogeneous(False)
		box.pack_start(hbox, True, True, 0)

		cnv7 = Gtk.RadioButton.new_with_label_from_widget(None, "CryptoNightV7")
		cnv7.connect("toggled", self.on_algo_toggled, "")
		hbox.pack_start(cnv7, False, False, 0)
		if algo == "":
			cnv7.set_active(True)
		else:
			cnv7.set_active(False)

		cnlite = Gtk.RadioButton.new_from_widget(cnv7)
		cnlite.set_label("CryptoNight-Lite")
		cnlite.connect("toggled", self.on_algo_toggled, " -a cryptonight-lite")
		hbox.pack_start(cnlite, False, False, 0)
		if algo == " -a cryptonight-lite":
			cnlite.set_active(True)

		cnheavy = Gtk.RadioButton.new_with_mnemonic_from_widget(cnv7,
		"CryptoNight-Heavy")
		cnheavy.connect("toggled", self.on_algo_toggled, " -a cryptonight-heavy")
		hbox.pack_start(cnheavy, False, False, 0)
		if algo == " -a cryptonight-heavy":
			cnheavy.set_active(True)

		self.button = Gtk.Button(label="Apply")
		self.button.connect("clicked", self.on_button_clicked)
		box.pack_start(self.button, True, True, 0)

		self.add(box)
	def on_button_clicked(self, button):
		global xwallet, xpool1
		xwallet = self.xwal.get_text()
		xpool1 = self.xpool.get_text()
		self.destroy()
	def on_devfeeoff_activated(self, switch, gparam):
		global devfeeoff
		if switch.get_active():
			devfeeoff = True
		else:
			devfeeoff = False
	def on_algo_toggled(self, button, name):
		global algo
		if button.get_active():
			algo = name

class DialogWindow(Gtk.Dialog): # dialog window

	def __init__(self, parent):
		global errortext, error
		Gtk.Dialog.__init__(self, error, parent, 0, # header
		(Gtk.STOCK_OK, Gtk.ResponseType.OK))

		self.set_default_size(150, 100)

		label = Gtk.Label(errortext) # window text

		box = self.get_content_area()
		box.add(label)
		self.show_all()

class InstallMinerWindow(Gtk.Window): # miners install window
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="Miners installation")
		global progressbar
		self.set_border_width(10)

		self.set_default_size(150, 100)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		self.add(box)
		label = Gtk.Label("The newest miners which were chosen by you will be installed now.")
		box.pack_start(label, True, True, 0)
		self.progressbar = Gtk.ProgressBar()
		self.progressbar.set_show_text(True)
		box.pack_start(self.progressbar, True, True, 0)

		self.buttonstart = Gtk.Button(label="Start!")
		self.buttonstart.connect("clicked", self.on_buttonstart_clicked)
		box.pack_start(self.buttonstart, True, True, 0)
		self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
		self.activity_mode = False

	def on_timeout(self, user_data): # edit progresspar on timeout
		global progr, prortext, dialrun
		self.progressbar.set_fraction(progr)
		self.progressbar.set_text(progrtext)
		if dialrun == True:
			dialog = DialogWindow(self)
			dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS) 
			dialog.set_resizable(False)
			dialog.run()
			dialog.destroy()
			quit() # quit after dialog was closed
		return True
	def on_buttonstart_clicked(self, button): # starting installation thread
		ProgressThread().start()
		self.buttonstart.set_sensitive(False)

class LabelWindow(Gtk.Window): # main window
	def __init__(self):
		Gtk.Window.__init__(self, title="Miners installation")
		self.set_border_width(10)
		hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		hbox.set_homogeneous(False)
		label = Gtk.Label()
		label.set_markup("<big>Hello!</big>\n"
				  "This tool will help you with mining configuration.\n"
				  "Please, configure miners before installation!\n"
				  "What miners you want install?\n")
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

		label = Gtk.Label()
		label.set_text("The user for whom tool are installing software")
		wbox.pack_start(label, True, True, 0)

		self.username = Gtk.Entry()
		wbox.pack_start(self.username, True, True, 0)

		self.button1 = Gtk.Button(label="Install!")
		self.button1.connect("clicked", self.on_button1_clicked)
		hbox.pack_start(self.button1, True, True, 0)

		self.add(hbox)
	
	def on_ethminer_activated(self, switch, gparam):
		global ethminer 
		if switch.get_active(): 
			ethminer = True
			self.button.set_sensitive(True)
		else:
			ethminer = False
			self.button.set_sensitive(False)
	def on_ethconf_clicked(self, button):
		ethconf = EthminerConfigWindow(self)
		ethconf.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		ethconf.set_resizable(False)
		ethconf.set_default_size(300, 250)
		ethconf.props.destroy_with_parent = False
		ethconf.show_all()
	def on_xmrig_activated(self, switch, gparam):
		global xmrig
		if switch.get_active():
			xmrig = True
			self.button2.set_sensitive(True)
		else:
			xmrig = False
			self.button2.set_sensitive(False)
	def on_xmrconf_clicked(self, button):
		xmrconf = XmrigConfigWindow(self)
		xmrconf.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		xmrconf.set_resizable(False)
		xmrconf.set_default_size(300, 250)
		xmrconf.props.destroy_with_parent = False
		xmrconf.show_all()
	def on_button1_clicked(self, button):
		global desktop, user, errortext
		user = self.username.get_text()
		desktop = "/home/" + self.username.get_text()
		
		pp = os.popen("ls /home | grep -w '" + self.username.get_text() + "'")
		time.sleep(0.1)
		if (pp.read()) == "":
			errortext = "Cannot identify this user!"
			dialog = DialogWindow(self)
			dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
			dialog.set_resizable(False)
			dialog.run()
			dialog.destroy()
		else:
			if ethminer == False and xmrig == False:
				errortext = "There are no miners for installation!"
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
window = LabelWindow()
window.set_default_size(400, 60)
window.set_default_icon_from_file('gpu.png')
window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
window.set_resizable(False)
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
