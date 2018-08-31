import gi, os, time
from threading import Thread
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
isroot = False # variable for checking - is user root?
pp = os.popen("whoami") # user identify command
time.sleep(0.1)
whoami = pp.read()
class MenuWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="FEMU - Free & Easy Mining on Ubuntu")
		global progressbar
		self.set_border_width(10)
		self.set_default_icon_from_file('gpu.png')
		self.set_default_size(150, 100)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)

		self.buttondriver = Gtk.Button(label="Drivers installation")
		self.buttondriver.connect("clicked", self.on_buttondriver_clicked)
		box.pack_start(self.buttondriver, True, True, 0)

		self.buttonminer = Gtk.Button(label="Miners installation")
		self.buttonminer.connect("clicked", self.on_buttonminer_clicked)
		box.pack_start(self.buttonminer, True, True, 0)
		
		self.buttonamdoc = Gtk.Button(label="AMD GPUs Overclocking")
		self.buttonamdoc.connect("clicked", self.on_buttonamdoc_clicked)
		box.pack_start(self.buttonamdoc, True, True, 0)

		self.buttonabout = Gtk.Button(label="About")
		self.buttonabout.connect("clicked", self.on_abtdlg)
		box.pack_start(self.buttonabout, True, True, 0)

		self.add(box)
	def on_buttonamdoc_clicked(self, button):
		os.popen("./amd_oc.out")		
	def on_buttondriver_clicked(self, button):
		os.popen("./driver_installer.out")
	def on_buttonminer_clicked(self, button):
		os.popen("./miner_installer.out")
	def on_abtdlg(self, button):
		about = Gtk.AboutDialog(self)
		about.set_logo(GdkPixbuf.Pixbuf.new_from_file("gpu.png"))
		about.set_program_name("FEMU - Free & Easy Mining on Ubuntu")
		about.set_version("v0.2 beta")
		about.set_copyright("© arkdlite 2018")
		about.set_comments("This tool was created for easy configuration Ubuntu for cryptocurrency mining without any difficulties for miners-beginners. If you find this program useful, than you can make a donation for author. Thanks!\nBTC: 1DtJutLDmH1MzY7Ew36ziLPp3YNuwXpvfb\nDASH: XqMYsGQyLGzr76cQXd7LHD6VEi13xRnm47\nZEC: t1eFez4MmkQALbhEGSFLcLERCZT3MM7KFQB\nXMR: 421cec4uww4hRKZUrmbxRBhTPqRXmb6PCFcyuakwmdr3ThcanQtoqQCPHSAWC4PPZfjAN6tt5yx7rSQf25SyTKhdFcsBaWK")
		about.run()
		about.destroy()
if "root" in whoami:
	isroot = True # checking - is user root?
if isroot == False:
	os.popen("lxqt-sudo ./main.out") # if user not root then quit
	quit()
window = MenuWindow() # main window
window.set_default_size(400, 60) # window size
window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
window.set_resizable(False)
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
