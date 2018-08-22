import gi, os, time
from threading import Thread
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
reb = False # variable for reboot
progr = 0.0 # variable for progressbar
amd = False
nvidia = False
progrtext = ""
class ProgressThread(Thread): # install thread
	def run(self):
		if amd == True: # if AMD selected
			global reb, progr, progrtext	
			progr = 0.01 # setting progress to 1%
			progrtext = "Downloading"
			director = str(os.getcwd())
			director = director + "/amdgpu-pro-install.bash --step1"
			os.system(director)
			progr = 0.2
			progrtext = "Unpacking files"
			director = str(os.getcwd())
			director = director + "/amdgpu-pro-install.bash --step2"
			os.system(director)
			progr = 0.4
			progrtext = "Running installation script"
			director = str(os.getcwd())
			director = director + "/amdgpu-pro-install.bash --step3"
			os.system(director)
			progr = 1.0
			reb = True
		if nvidia == True: # if nvidia selected
			progr = 0.5
			director = str(os.getcwd())
			director = director + "/nvidia-current-install.bash"
			os.system(director)
			os.popen("software-properties-gtk")
			progr = 1.0 
			Gtk.main_quit()
class DialogWindow(Gtk.Dialog): # error window

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
		global progressbar
		self.set_border_width(10)

		self.set_default_size(150, 100)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		self.add(box)
		label = Gtk.Label("Driver have been installed. Please, reboot the computer.")
		box.pack_start(label, True, True, 0)
		self.button = Gtk.Button(label="Reboot")
		self.button.connect("clicked", self.on_button_clicked)
		box.pack_start(self.button, True, True, 0)
		
	def on_button_clicked(self, button):
		os.system("reboot") 

class InstallNvidiaWindow(Gtk.Window):
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="Driver installation")
		global progressbar
		self.set_border_width(10)

		self.set_default_size(150, 100)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		self.add(box)
		label = Gtk.Label()
		label.set_markup("The newest version of Nvidia driver will be added to\n"
				"repositories list. Than standard Ubuntu tool will be\n"
				"run. To start installation please click 'Additional \n"
				"drivers'. Next, choose the newest version of Nvidia driver\n"
				"and install this. After that reboot this computer.")
		box.pack_start(label, True, True, 0)
		self.progressbar = Gtk.ProgressBar()
		box.pack_start(self.progressbar, True, True, 0)

		self.button = Gtk.Button(label="OK")
		self.button.connect("clicked", self.on_button_clicked)
		box.pack_start(self.button, True, True, 0)
		self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
		self.activity_mode = False

	def on_timeout(self, user_data):
		global progr
		self.progressbar.set_fraction(progr)
		return True
	def on_button_clicked(self, button):	
		ProgressThread().start()
		self.button.set_sensitive(False)
class InstallAMDWindow(Gtk.Window):
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="Driver installation")
		global progressbar
		self.set_border_width(10)

		self.set_default_size(150, 100)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		self.add(box)
		label = Gtk.Label("The newest AMDGPU-PRO driver will be downloaded and installed.")
		box.pack_start(label, True, True, 0)
		self.progressbar = Gtk.ProgressBar()
		box.pack_start(self.progressbar, True, True, 0)

		self.button = Gtk.Button(label="Start")
		self.button.connect("clicked", self.on_button_clicked)
		box.pack_start(self.button, True, True, 0)
		self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
		self.activity_mode = False

	def on_timeout(self, user_data):
		global reb
		if reb == True:
			reboot = RebootWindow(self)
			reboot.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
			reboot.set_resizable(False)
			reboot.show_all()
			reb = False
		global progr, prortext
		self.progressbar.set_fraction(progr)
		self.progressbar.set_text(progrtext)
		return True
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
		global nvidia
		if switch.get_active():
			nvidia = True
			self.amdswitch.set_active(False)	
		else:
			nvidia = False
	def on_amd_activated(self, switch, gparam):
		global amd
		if switch.get_active():
			amd = True
			self.nvswitch.set_active(False)		
		else:
			amd = False
	def on_button_clicked(self, button):
		def progress_timeout(val):
			global progressbar
			progressbar.set_fraction(val)
		if amd == False and nvidia == False:
			dialog = DialogWindow(self)
			dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
			dialog.set_resizable(False)
			dialog.run()
			dialog.destroy()
		if amd == True:
			install = InstallAMDWindow(self)
			install.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
			install.set_resizable(False)
			install.show_all()
		if nvidia == True:
			install = InstallNvidiaWindow(self)
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
