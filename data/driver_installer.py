import gi, os, time
from threading import Thread
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
reb = False #объявление переменной для перезагрузки
progr = 0.0 #объявление переменной прогрессбара
amd = False #объявление переменных для Nvidia и AMD
nvidia = False
progrtext = "" #объявление переменной текста прогрессбара
class ProgressThread(Thread): #класс, отвечающий за прогрессбар, создается поток
	def run(self):
		if amd == True: #если выбраны драйверы AMD
			global reb, progr, progrtext	
			progr = 0.01 #ставим прогресс на 1%
			progrtext = "Загрузка драйвера"
			director = str(os.getcwd()) #записываем в переменную текущую директорию
			director = director + "/amdgpu-pro-install.bash --step1" #получаем расположение необходимого скрипта
			os.system(director) #запускаем скрипт
			progr = 0.2 #по аналогии
			progrtext = "Извлечение файлов"
			director = str(os.getcwd())
			director = director + "/amdgpu-pro-install.bash --step2"
			os.system(director)
			progr = 0.4
			progrtext = "Исполнение скрипта установки"
			director = str(os.getcwd())
			director = director + "/amdgpu-pro-install.bash --step3"
			os.system(director)
			progr = 1.0
			reb = True
		if nvidia == True: #если выбраны драйверы Nvidia
			progr = 0.5 #по аналогии с AMD запускаем скрипт
			director = str(os.getcwd())
			director = director + "/nvidia-current-install.bash"
			os.system(director)
			os.popen("software-properties-gtk") #открываем "Программы и обновления"
			progr = 1.0 
			Gtk.main_quit() #выход
class DialogWindow(Gtk.Dialog): #окно ошибке в случае, если ничего не выбрано

	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "Ошибка!", parent, 0, #заголовок окна
		(Gtk.STOCK_OK, Gtk.ResponseType.OK))

		self.set_default_size(150, 100)

		label = Gtk.Label("Для установки ничего не выбрано!") #текст окна

		box = self.get_content_area()
		box.add(label) #добавить текст
		self.show_all()
class RebootWindow(Gtk.Window): #окно с предложением перезагрузки
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="Установка драйверов")
		global progressbar
		self.set_border_width(10)

		self.set_default_size(150, 100)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		self.add(box)
		label = Gtk.Label("Драйверы установлены. Необходима перезагрузка.")
		box.pack_start(label, True, True, 0)
		self.button = Gtk.Button(label="Перезагрузить") #кнопка Перезагрузить
		self.button.connect("clicked", self.on_button_clicked)
		box.pack_start(self.button, True, True, 0)
		
	def on_button_clicked(self, button): #если кнопка нажата, то перезагрузить
		os.system("reboot") 



class InstallNvidiaWindow(Gtk.Window): #окно установки драйверов Nvidia
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="Установка драйверов")
		global progressbar
		self.set_border_width(10)

		self.set_default_size(150, 100)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		self.add(box)
		label = Gtk.Label()
		label.set_markup("В список репозиториев будут добавлены новейшие версии\n"
				"драйвера Nvidia. После этого будет запущена стандартная\n"
				"утилита Ubuntu 'Программы и обновления'. Чтобы начать\n"
				"установку, необходимо перейти на вкладку 'Дополнительные\n"
				"драйверы' и выбрать самую свежую версию для установки.\n"
				"Когда установка завершится, необходимо будет перезагрузить\n"
				"компьютер.")
		box.pack_start(label, True, True, 0)
		self.progressbar = Gtk.ProgressBar() #прогрессбар
		box.pack_start(self.progressbar, True, True, 0)

		self.button = Gtk.Button(label="Понятно")
		self.button.connect("clicked", self.on_button_clicked)
		box.pack_start(self.button, True, True, 0)
		self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
		self.activity_mode = False

	def on_timeout(self, user_data):
		global progr
		self.progressbar.set_fraction(progr) #назначение прогрессбару значения каждый N-ый промежуток времени
		return True
	def on_button_clicked(self, button):	
		ProgressThread().start() #вызов потока для обработки с=установочных скриптов
		self.button.set_sensitive(False) #деактивация кнопки
class InstallAMDWindow(Gtk.Window):
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="Установка драйверов")
		global progressbar
		self.set_border_width(10)

		self.set_default_size(150, 100)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		self.add(box)
		label = Gtk.Label("Будет загружен и установлен новейший драйвер AMDGPU-PRO.")
		box.pack_start(label, True, True, 0)
		self.progressbar = Gtk.ProgressBar()
		box.pack_start(self.progressbar, True, True, 0)

		self.button = Gtk.Button(label="Начать")
		self.button.connect("clicked", self.on_button_clicked)
		box.pack_start(self.button, True, True, 0)
		self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
		self.activity_mode = False

	def on_timeout(self, user_data):
		global reb
		if reb == True: #если дана команда перезагрузки, то открыть окно с предложением
			reboot = RebootWindow(self)
			reboot.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
			reboot.set_resizable(False)
			reboot.show_all()
			reb = False
		global progr, prortext
		self.progressbar.set_fraction(progr) #установка значения прогрессбара
		self.progressbar.set_text(progrtext)
		return True
	def on_button_clicked(self, button):
		ProgressThread().start()
		self.button.set_sensitive(False)
class LabelWindow(Gtk.Window):
	
	def __init__(self):
		Gtk.Window.__init__(self, title="Установка драйверов")
		self.set_border_width(10)
		hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		hbox.set_homogeneous(False)
		label = Gtk.Label()
		label.set_markup("<big>Привет!</big>\n"
				  "Эта программа поможет тебе настроить майнинг.\n"
				  "Выбери, какие драйверы установить:\n")
		label.set_justify(Gtk.Justification.FILL)
		hbox.pack_start(label, True, True, 0)

		vbox = Gtk.Box(spacing=6)
		vbox.set_homogeneous(False)
		hbox.pack_start(vbox, True, True, 0)

		label = Gtk.Label()
		label.set_markup("<big>Nvidia</big>\n")
		label.set_justify(Gtk.Justification.FILL)
		vbox.pack_start(label, True, True, 0)
		self.nvswitch = Gtk.Switch() #переключатель Nvidia
		self.nvswitch.connect("notify::active", self.on_nvidia_activated)
		self.nvswitch.set_active(False)
		vbox.pack_start(self.nvswitch, True, True, 0)
		
		label = Gtk.Label()
		label.set_markup("<big>AMD</big>\n")
		label.set_justify(Gtk.Justification.FILL)
		vbox.pack_start(label, True, True, 0)
		self.amdswitch = Gtk.Switch() #переключатель AMD
		self.amdswitch.connect("notify::active", self.on_amd_activated)
		self.amdswitch.set_active(False)
		vbox.pack_start(self.amdswitch, True, True, 0)

		mbox = Gtk.Box(spacing=6)
		mbox.set_homogeneous(False)
		hbox.pack_start(mbox, True, True, 0)

		
		self.button = Gtk.Button(label="Установить!")
		self.button.connect("clicked", self.on_button_clicked)
		mbox.pack_start(self.button, True, True, 0)


		self.add(hbox)
	def on_nvidia_activated(self, switch, gparam):
		global nvidia
		if switch.get_active(): #если Nvidia включен, выключить AMD
			nvidia = True
			self.amdswitch.set_active(False)	
		else:
			nvidia = False
	def on_amd_activated(self, switch, gparam):
		global amd
		if switch.get_active(): #если AMD включен, выключить Nvidia
			amd = True
			self.nvswitch.set_active(False)		
		else:
			amd = False
	def on_button_clicked(self, button):
		def progress_timeout(val):
			global progressbar
			progressbar.set_fraction(val)
			#return True
		if amd == False and nvidia == False: #показать окно ошибки, если драйвер не выбран
			dialog = DialogWindow(self)
			dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS) #показать окно всегда по центру экрана
			dialog.set_resizable(False)
			dialog.run()
			dialog.destroy()
		if amd == True: #показать окно установки драйвера AMD
			install = InstallAMDWindow(self)
			install.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
			install.set_resizable(False)
			install.show_all()
		if nvidia == True: #показать окно установки драйвера Nvidia
			install = InstallNvidiaWindow(self)
			install.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
			install.set_resizable(False)
			install.show_all()
window = LabelWindow() #главное окно
window.set_default_size(400, 60) #размер гланого окна
window.set_default_icon_from_file('gpu.png')
window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
window.set_resizable(False)
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
