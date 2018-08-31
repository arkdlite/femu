import gi, os, time
from threading import Thread
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
# переменные для параметров Ethminer
nvidia = False
amd = True
devfeeoff = False
ethminer = False
ethminerssl = False
ethminerbuild = False
ewallet = ""
epool1 = ""
stratumtype = "stratum"
# переменные для параметров XMRig-AMD
xmrig = False
xwallet = ""
xpool1 = ""
algo = ""
user = "" # объявление переменной для имени пользователя, для которого ведется установка
errortext = "" # объявление переменной текста диалога с ошибкой
errorhead = "Ошибка!" # объявление переменной заголовка диалога с ошибкой
progr = 0.0 # объявление переменной прогресса прогрессбара
progrtext = "" # объявление переменной текста прогрессбара
dialrun = False # объявление переменной запуск диалога

def runcmd(cmd):
	os.system(cmd + " >> /var/log/femu.log 2>&1")

class ProgressThread(Thread): #класс, отвечающий за запуск скриптов
	def run(self):
		#сбор всех глобальных переменных
		global progr, progrtext, desktop, stratumtype, ethminerssl, ewallet, epool1, amd, nvidia, user, ethminerbuild, algo, xwallet, xpool1, devfeeoff, errorhead, errortext, dialrun
		director = str(os.getcwd()) # сохраняем текущую директорию
		progr = 0.01 #ставим прогресс на 1%
		progrtext = "Загрузка майнера" # установка текста прогрессбара
		work = director + "/miner-install.bash --step1 " + desktop 
		runcmd(work) # запуск скрипта с передачей текущей директории
		progrtext = "Извлечение файлов"
		progr = 0.05
		progrtext = "Исполнение скрипта установки"
		if ethminer == True: # действия, если Ethminer активирован
			if ethminerssl == True: # определение типа соединения
				ssl = "ssl"
			else:
				ssl = "tcp"
			if ethminerbuild == True: # запуск скрипта оптимизированной сборки, если необходимо
				work = director + "/miner-install.bash --ethminer-build " + desktop + "/miners"
				runcmd(work)
				progr = 0.5
				progrtext = "Сборка Ethminer"
				work = director + "/miner-install.bash --ethminer-build2 " + desktop + "/miners"
				runcmd(work)
				progr = 0.99
			else: # обычное скачивание релиза с GitHub
				work = director + "/miner-install.bash --ethminer-bin " + desktop + "/miners"
				runcmd(work)
				progr = 0.99
			# создание файла для скрипта запуска майнера
			work = director + "/miner-install.bash --step2 " + desktop + "/ethminer.bash"
			runcmd(work)
			# определение типа видеокарт для Ethminer
			if nvidia == True and amd == False:
				mode = "-U"
			if nvidia == True and amd == True:
				mode = "-X"
			if nvidia == False and amd == True:
				mode = "-G"
			# наполнение скрипта запуска
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
		if xmrig == True: # действия, если XMRig-AMD активирован
			progr = 0.01
			progrtext = "Установка зависимостей и обновление системы"
			work = director + "/miner-install.bash --step1xmr " + desktop + "/miners"
			runcmd(work)
			progr = 0.1
			progrtext = "Загрузка майнера XMRig"
			work = director + "/miner-install.bash --step2xmr " + desktop + "/miners"
			runcmd(work)
			progr = 0.15
			if devfeeoff == True: # отключение комиссии, если требуется
				progrtext = "Отключение комиссии XMRig"
				work = director + "/miner-install.bash --devfeeoff " + desktop + "/miners"
				runcmd(work)
				progr = 0.16
			progrtext = "Подготовка к сборке майнера XMRig"
			work = director + "/miner-install.bash --step3xmr " + desktop + "/miners"
			runcmd(work)
			progr = 0.3
			progrtext = "Сборка майнера XMRig"
			work = director + "/miner-install.bash --step4xmr " + desktop
			runcmd(work)
			progr = 0.97
			progrtext = "Настройка запуска XMRig"
			work = "echo '#!/bin/bash' > %s" % desktop + "/xmrig-amd.bash" # наполнение скрипта запуска
			runcmd(work)	
			if devfeeoff == True:
				work = "echo '%s/miners/xmrig-amd/xmrig-amd%s -l xmrig.log --donate-level 0 --api-port 4444 -o %s -u %s -p x --variant 1 -k' >> %s" % (desktop, algo, xpool1, xwallet, desktop + "/xmrig-amd.bash")
			else:
				work = "echo '%s/miners/xmrig-amd/xmrig-amd%s -l xmrig.log --donate-level 1 --api-port 4444 -o %s -u %s -p x --variant 1 -k' >> %s" % (desktop, algo, xpool1, xwallet, desktop + "/xmrig-amd.bash")
			runcmd(work)	# назначение скрипту прав доступа, чтобы пользователь мог его изменять и запускать			
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
		# выдача диалога о завершении установки
		errorhead = "Успешно!"
		errortext = "ПО для майнинга установлено.\nВсе майнеры добавлены в скрипт автозапуска.\nЖелаю добыть побольше монеток!\nНажми 'ОК', чтобы выйти."
		dialrun = True
class EthminerConfigWindow(Gtk.Window): # окно настройки Ethminer
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="Настройки Ethminer")
		global ewallet, epool1, stratumtype, ethminerbuild
		self.set_border_width(10)
		self.set_default_size(300, 250)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		label = Gtk.Label()
		label.set_markup("Для каких видеокарт проводится установка?")
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
		label.set_text("Использовать сборку из исходного кода\n"
				"с использованем новейших компиляторов,\n"
				"пересобрать ядра AMD. Даёт больше\n"
				"хешрейта. Если не жалко времени - включи!")
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
		label.set_text("Адрес пула:")
		box.pack_start(label, True, True, 0)
		self.epool = Gtk.Entry()
		if epool1 == "":
			self.epool.set_text("example.com:1234")
		else:
			self.epool.set_text(epool1)
		box.pack_start(self.epool, True, True, 0)
		label = Gtk.Label()
		label.set_text("Кошелек (логин пула):")
		box.pack_start(label, True, True, 0)
		self.ewal = Gtk.Entry()
		box.pack_start(self.ewal, True, True, 0)
		if ewallet == "":
			self.ewal.set_text("0x1245...")
		else:
			self.ewal.set_text(ewallet)
		label = Gtk.Label()
		label.set_text("Тип stratum (посмотри на пуле):")
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
		self.button = Gtk.Button(label="Применить")
		self.button.connect("clicked", self.on_button_clicked)
		box.pack_start(self.button, True, True, 0)
		self.add(box)
	def on_button_clicked(self, button): # если кнопка нажата, сохранить настройки и закрыть окно
		global ewallet, epool1
		ewallet = self.ewal.get_text()	
		epool1 = self.epool.get_text()
		self.destroy()
	def on_nvidia_activated(self, switch, gparam):
		global nvidia, amd
		if switch.get_active():
			nvidia = True
			self.buildswitch.set_active(False) # выключение возможности сборки Ethminer для Nvidia
			self.buildswitch.set_sensitive(False)
			ethminerbuild = False
		else:
			if not self.amdswitch.get_active(): # если ничего не выбрано, принудительно включить AMD
				self.amdswitch.set_active(True)
				amd = True
			nvidia = False
			self.buildswitch.set_sensitive(True)
	def on_amd_activated(self, switch, gparam):
		global nvidia, amd
		if switch.get_active():
			amd = True
		else: # если ничего не выбрано, принудительно включить Nvidia
			if not self.nvswitch.get_active():
				self.nvswitch.set_active(True)
				nvidia = True
			amd = False
	def on_build_activated(self, switch, gparam):
		global ethminerbuild # обработка нажатия переключателя сборки Ethminer
		if switch.get_active():
			ethminerbuild = True
		else:
			ethminerbuild = False
	def on_stratum_toggled(self, button, name):
		global stratumtype # обработка выбора типа stratum
		if button.get_active():
			stratumtype = name
	def on_ssl_activated(self, switch, gparam):
		global ethminerssl # обработка выбора SSL 
		if switch.get_active():
			ethminerssl = True
		else:
			ethminerssl = False
		
class XmrigConfigWindow(Gtk.Window): # окно настроек XMRig-AMD
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="Настройки XMRig-AMD")
		global xwallet, xpool1, devfeeoff, algo
		self.set_border_width(10)
		self.set_default_size(300, 250)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		label = Gtk.Label()
		label.set_markup("Установка может проводиться только для видеокарт AMD\nЕсли у вас не установлены драйверы AMD, то это вызовет ошибку!")
		box.pack_start(label, True, True, 0)
		hbox = Gtk.Box(spacing=6)
		hbox.set_homogeneous(False)
		box.pack_start(hbox, True, True, 0)
		label = Gtk.Label()
		label.set_text("Отключить devfee майнера (разработчик XMRig\nхотел бы, чтобы в случае отключения комиссии ему\nотправили пожертвование, адреса XMR и BTC см. на\nGitHub, введя в поиск 'xmrig-amd')")
		hbox.pack_start(label, True, True, 0)
		self.devfeeswitch = Gtk.Switch()
		self.devfeeswitch.connect("notify::active", self.on_devfeeoff_activated)
		if devfeeoff == True:
			self.devfeeswitch.set_active(True)
		else:
			self.devfeeswitch.set_active(False)
		hbox.pack_start(self.devfeeswitch, True, True, 0)
		label = Gtk.Label()
		label.set_text("Адрес пула:")
		box.pack_start(label, True, True, 0)
		self.xpool = Gtk.Entry()
		if xpool1 == "":
			self.xpool.set_text("example.com:1234")
		else:
			self.xpool.set_text(xpool1)
		box.pack_start(self.xpool, True, True, 0)
		label = Gtk.Label()
		label.set_text("Кошелек (логин пула):")
		box.pack_start(label, True, True, 0)
		self.xwal = Gtk.Entry()
		box.pack_start(self.xwal, True, True, 0)
		if xwallet == "":
			self.xwal.set_text("4abcd...")
		else:
			self.xwal.set_text(xwallet)
		label = Gtk.Label()
		label.set_text("Алгоритм:")
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
		self.button = Gtk.Button(label="Применить")
		self.button.connect("clicked", self.on_button_clicked)
		box.pack_start(self.button, True, True, 0)
		self.add(box)
	def on_button_clicked(self, button):
		global xwallet, xpool1
		xwallet = self.xwal.get_text()
		xpool1 = self.xpool.get_text()
		self.destroy()
	def on_devfeeoff_activated(self, switch, gparam):
		global devfeeoff # обработка нажатия переключателя выключения комиссии
		if switch.get_active():
			devfeeoff = True
		else:
			devfeeoff = False
	def on_algo_toggled(self, button, name):
		global algo # обработка нажатия переключателя алгоритмов
		if button.get_active():
			algo = name
class DialogWindow(Gtk.Dialog): # диалоговое окно
	def __init__(self, parent):
		global errortext, error
		Gtk.Dialog.__init__(self, error, parent, 0, #заголовок окна
		(Gtk.STOCK_OK, Gtk.ResponseType.OK))
		self.set_default_size(150, 100)
		label = Gtk.Label(errortext) #текст окна
		box = self.get_content_area()
		box.add(label)
		self.show_all()
class InstallMinerWindow(Gtk.Window): # окно установки майнеров
	def __init__(self, parent):
		Gtk.Window.__init__(self, title="Установка майнеров")
		global progressbar
		self.set_border_width(10)
		self.set_default_size(150, 100)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		box.set_homogeneous(False)
		self.add(box)
		label = Gtk.Label("Будут загружены и установлены майнеры в соответствии с указанными настройками.")
		box.pack_start(label, True, True, 0)
		self.progressbar = Gtk.ProgressBar()
		self.progressbar.set_show_text(True)
		box.pack_start(self.progressbar, True, True, 0)
		self.buttonstart = Gtk.Button(label="Начать")
		self.buttonstart.connect("clicked", self.on_buttonstart_clicked)
		box.pack_start(self.buttonstart, True, True, 0)
		self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
		self.activity_mode = False
	def on_timeout(self, user_data): # при таймауте ставить значения прогрессбара
		global progr, prortext, dialrun
		self.progressbar.set_fraction(progr) #установка значения прогрессбара
		self.progressbar.set_text(progrtext)
		if dialrun == True:
			dialog = DialogWindow(self)
			dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS) #показать окно всегда по центру экрана
			dialog.set_resizable(False)
			dialog.run()
			dialog.destroy()
			quit() # выход после закрытия диалога
		return True
	def on_buttonstart_clicked(self, button): # старт потока установки
		ProgressThread().start()
		self.buttonstart.set_sensitive(False)
class LabelWindow(Gtk.Window): # главное окно
	def __init__(self):
		Gtk.Window.__init__(self, title="Установка майнеров")
		self.set_border_width(10)
		hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		hbox.set_homogeneous(False)
		label = Gtk.Label()
		label.set_markup("<big>Привет!</big>\n"
				  "Эта программа поможет тебе настроить майнинг.\n"
				  "Обязательно настрой майнеры перед установкой!\n"
				  "Выбери, какие майнеры установить:\n")
		label.set_justify(Gtk.Justification.FILL)
		hbox.pack_start(label, True, True, 0)
		vbox = Gtk.Box(spacing=6)
		vbox.set_homogeneous(False)
		hbox.pack_start(vbox, True, True, 0)
		label = Gtk.Label()
		label.set_markup("<big>  Ethminer  </big>\n")
		label.set_justify(Gtk.Justification.FILL)
		vbox.pack_start(label, True, True, 0)
		self.ethswitch = Gtk.Switch() #переключатель Ethminer
		self.ethswitch.connect("notify::active", self.on_ethminer_activated)
		self.ethswitch.set_active(False)
		vbox.pack_start(self.ethswitch, True, True, 0)
		self.button = Gtk.Button(label="Настроить")
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
		self.xmrswitch = Gtk.Switch() #переключатель XMRig-AMD
		self.xmrswitch.connect("notify::active", self.on_xmrig_activated)
		self.xmrswitch.set_active(False)
		qbox.pack_start(self.xmrswitch, True, True, 0)
		self.button2 = Gtk.Button(label="Настроить")
		self.button2.connect("clicked", self.on_xmrconf_clicked)
		self.button2.set_sensitive(False)
		qbox.pack_start(self.button2, True, True, 0)
		wbox = Gtk.Box(spacing=6)
		wbox.set_homogeneous(False)
		hbox.pack_start(wbox, True, True, 0)
		label = Gtk.Label()
		label.set_text("Имя пользователя, для которого\nпроводится установка:")
		wbox.pack_start(label, True, True, 0)
		self.username = Gtk.Entry()
		wbox.pack_start(self.username, True, True, 0)
		self.button1 = Gtk.Button(label="Установить!")
		self.button1.connect("clicked", self.on_button1_clicked)
		hbox.pack_start(self.button1, True, True, 0)
		self.add(hbox)
	
	def on_ethminer_activated(self, switch, gparam):
		global ethminer 
		if switch.get_active(): # назначение чувствительности кнопки конфигурации
			ethminer = True
			self.button.set_sensitive(True)
		else:
			ethminer = False
			self.button.set_sensitive(False)
	def on_ethconf_clicked(self, button): # открытие окна конфигурации Ethminer
		ethconf = EthminerConfigWindow(self)
		ethconf.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		ethconf.set_resizable(False)
		ethconf.set_default_size(300, 250)
		ethconf.props.destroy_with_parent = False
		ethconf.show_all()
	def on_xmrig_activated(self, switch, gparam):
		global xmrig
		if switch.get_active(): # назначение чувствительности кнопки конфигурации
			xmrig = True
			self.button2.set_sensitive(True)
		else:
			xmrig = False
			self.button2.set_sensitive(False)
	def on_xmrconf_clicked(self, button): # открытие окна конфигурации XMRig-AMD
		xmrconf = XmrigConfigWindow(self)
		xmrconf.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		xmrconf.set_resizable(False)
		xmrconf.set_default_size(300, 250)
		xmrconf.props.destroy_with_parent = False
		xmrconf.show_all()
	def on_button1_clicked(self, button): # проверка на ошибки
		global desktop, user, errortext
		user = self.username.get_text()
		desktop = "/home/" + self.username.get_text()
		
		pp = os.popen("ls /home | grep -w '" + self.username.get_text() + "'")
		time.sleep(0.1)
		if (pp.read()) == "":
			errortext = "Пользователь не найден!"
			dialog = DialogWindow(self)
			dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS) #показать окно всегда по центру экрана
			dialog.set_resizable(False)
			dialog.run()
			dialog.destroy()
		else:
			if ethminer == False and xmrig == False:
				errortext = "Для установки ничего не выбрано!"
				dialog = DialogWindow(self)
				dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS) #показать окно всегда по центру экрана
				dialog.set_resizable(False)
				dialog.run()
				dialog.destroy()
			else: # старт установочного окна
				install = InstallMinerWindow(self)
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
