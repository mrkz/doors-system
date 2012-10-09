#!/usr/bin/env python
#coding=utf-8
"""\\
Aquí se contiene el código para la creación de la interfaz gráfica (gtk2)
Centro Universitario de Ciencias Exactas e Ingenierias."""

import string			# módulo para manejo de cadenas
import gtk				# módulo de las herramientas gtk (gimp tool kit)
import pygtk			# módulo de la interfaz pygtk
pygtk.require('2.0')	# se desea usar la versión 2.0 de PyGTK (2.x de gtk)
import gobject			# módulo para hacer los 'delay'
import time				# módulo para mostrar el reloj
import sys		 		# módulo para manejo de directorios (importar módulos creados)

# Módulo para manejo del puerto serial
import serial
from serial.tools import list_ports

sys.path.append('../src')

# se importan los módulos del programa
#
# form src.<module> import <class>
from src.database import Connection		# se importa clase para DB


class Window:
	# constructor
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.set_property()
		self.vBox = gtk.VBox(gtk.FALSE, 0)
		self.window.add(self.vBox)
		self.create_menubar()
		self.create_entry()
		self.create_clock()
		self.create_user_box()
		self.warning_flag = False
		self.create_status_bar()
		self.create_warning_lector()
		self.show()
		# parametros de clase Connection: <host>,<user>,<password>,<database>
		# sin parametros se conecta a DB local
		self.database = Connection()
		# rutina para abrir puerto serial del arduino
		self.connection_routine()
		# se crea una rutina que se ejecuta cada segundo para leer del arduino
		time = gobject.timeout_add(1000, self.read_id)

	# método para establecer propiedades de la ventana
	def set_property(self,
					 title = "Centro Universitario de Ciencias Exactas e Ingenierias",
					 width = 800, height = 600, resize = True):
		self.window.set_title(title)
		self.window.set_default_size(width,height)
		self.window.set_resizable(resize)
		# al presionar boton "cerrar" se envía señal 'destroy' y el programa se cierra
		self.window.connect("destroy",self.close_window)

	# método para crear la barra de menu
	def create_menubar(self):
		item_file = gtk.MenuItem("_Archivo") 
		menu_bar  = gtk.MenuBar()
		menu_bar.append(item_file)
		self.vBox.pack_start(menu_bar, gtk.FALSE, gtk.FALSE, 0)

	# método para creación de las entradas de texto
	def create_entry(self):
		HBox = gtk.HBox(gtk.FALSE, 0)
		self.vBox.pack_start(HBox, gtk.TRUE, gtk.FALSE, 50)
		label = gtk.Label()
		label.set_markup("<big><b>Presente Identificación</b></big>")
		label.set_use_markup(gtk.TRUE)
		HBox.pack_start(label, gtk.TRUE, gtk.FALSE, 0)
		self.entry = gtk.Entry()
		self.entry.connect("activate",self.callback_code,self.entry)
		HBox.pack_start(self.entry, gtk.TRUE, gtk.FALSE, 0)

	# método para escribir las etiquetas con datos de usuario
	def create_user_box(self):
		vBox = gtk.VBox(gtk.FALSE, 0)
		self.vBox.pack_start(vBox, gtk.TRUE, gtk.FALSE, 0)
		hBox = gtk.HBox(gtk.FALSE, 0)
		self.label_name = gtk.Label()
		hBox.pack_start(self.label_name, gtk.FALSE, gtk.FALSE, 50)
		vBox.pack_start(hBox, gtk.FALSE, gtk.FALSE, 10)

	# método para mostrar el reloj en pantalla
	def create_clock(self):
		vBox = gtk.VBox(gtk.TRUE, 0)
		self.vBox.pack_start(vBox, gtk.TRUE, gtk.FALSE, 0)
		self.clock = gtk.Label()
		vBox.pack_start(self.clock, gtk.TRUE, gtk.FALSE, 0)
		time = gobject.timeout_add(1000, self.display_current_time, self.clock)
	
	# método para crear una barra de estado	
	def create_status_bar(self):
		error_statusbar = """I/O error: lector device"""
		success_statusbar = """Funcionando :)"""
		vBox = gtk.VBox(gtk.FALSE, 0)
		self.vBox.pack_end(vBox, gtk.FALSE, gtk.FALSE, 0)
		self.status_bar = gtk.Statusbar()
		vBox.pack_start(self.status_bar, gtk.FALSE, gtk.FALSE, 0)
		self.error_status_bar   = self.status_bar.get_context_id(error_statusbar)
		self.success_status_bar = self.status_bar.get_context_id(success_statusbar)
	
	# método para conectar un arduino
	def connection_routine(self):
		
		# se filtran los dispositivos seriales que contengan
		# la cadena '0403:6001', esta es el PID del arduino
		# idVendor   	0x0403 Future Technology Devices International, Ltd
		# idProduct     0x6001 FT232 USB-Serial (UART) IC
		#
		#   idVendor	idProduct
		#	'0403	:	6001'

		
		# obtener lista de todos los arduinos disponibles
		available_ports = serial.tools.list_ports.grep('0403:6001') 
		# lista vacia
		arduinos = []
		for device in available_ports:
			# se añaden los arduinos disponibles
			arduinos.append(device)
		
		# si hay al menos un arduino conectado prosigue
		if len(arduinos) > 0:
			# si hay más de un arduino conectado, trata de conectarse
			for device in arduinos:
				try:
					# se toma el puerto del arduino conectado
					port = device[0]
					print arduinos
					print port
					# trata de crear conexión a arduino
					self.arduino = serial.Serial(port, baudrate=9600, timeout=0)
					self.arduino.write('1')
					# si se conectó al puerto exitosamente se termina la rutina de conexión
					if self.arduino.isOpen():
						print "connected on port: %s" % port
						print self.warning_flag
						# se cierra el warning del arduino
						if self.warning_flag == True:
							self.warning_arduino.destroy()
							self.warning_flag = False
						# cambia el mensaje de barra de estado
						self.statusbar_pop_item(self.error_status_bar)
						self.statusbar_push_item(self.success_status_bar,"""Funcionando :)""")
						break
			
				# si no existe el puerto no se crea instancia del objeto serial
				# y por tanto la variable self.arduino no está definida
				# lanzando una excepción NameError
				except NameError:
					print "Error: port %s doesn\'t exists" % port
			
				# si el puerto no se pudo abrir, se lanza la excepción
				#FIXME: El puerto se abrió pero se desconectó sin ser cerrado antes ↓↓
				# SerialException y se prosigue a conectar otros posibles arduinos
				except serial.serialutil.SerialException:
					print "Arduino desconectado violentamente >:("
#					self.arduino.close()
#					del self.arduino()
		else:
			if self.warning_flag == False:
				self.create_warning_lector()
			#TODO: mostrar mensaje de que no hay arduino conectado
			pass # temporal, hasta hacer el todo :v
	
	def create_warning_lector(self):
		# si no hay un dialogo de advertencia creado
		print "génesis del dialogo: ", self.warning_flag
		if self.warning_flag == False:
			warning_message = """Dispositivo lector no detectado"""
			self.warning_arduino = gtk.MessageDialog(self.window,flags = gtk.DIALOG_MODAL,
													 type=gtk.MESSAGE_WARNING,
													 buttons = gtk.BUTTONS_NONE,
													 message_format = warning_message)
			self.warning_arduino.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
			self.warning_arduino.set_transient_for(self.window)
			self.warning_flag = True
			self.warning_arduino.show()
			self.statusbar_push_item(self.error_status_bar, """Error: Dispositivo lector no detectado""")


	# método para mostrar ventana
	def show(self):
		self.window.show_all()
	
	# método para cerrar conexiones y cerrar ventana
	def close_window(self, widget = None):
		try:
			self.database.close()
			self.arduino.close()
		# si no hay arduino conectado y se cierra la ventana,
		# se lanza la excepción AttributeError por que la variable self.arduino
		# no existe
		except AttributeError:
			# no se hace nada
			pass
		gtk.main_quit()

########		Retrollamadas (Callbacks)		########

	# método para tratar entry del código
	def callback_code(self, data= None):
		code = self.string[1:-5]		# RFID
		print "leí:",code				# RFID
		if self.database.get_access(code, door = 1):
			self.display_user(code, "Sin Nombre aún :v")
			#TODO: mostrar datos del usuario en pantalla
			# se envía bit para apertura de chapa
			self.arduino.write('1')
		else:
			# Sin acceso
			self.display_user()
		#if code == "209365915":
		#	self.display_user(code, "<Nombre del usuario>")
		#else:
		#	self.display_user()
	
	# método para mostrar mensajes en la barra de estado
	def statusbar_push_item(self, context_id, string):
		self.status_bar.push(context_id, string)
	
	# método para eliminar mensaje de error la barra de estado
	def statusbar_pop_item(self, context_id):
	# contextos posibles:
	#  self.error_status_bar 
	#  self.success_status_bar
		self.status_bar.remove_all(context_id)
	
	# método para actualizar datos de usuario
	def display_user(self, code = None, name = None):
		if code and name:
			self.label_name.set_markup("<big><big><big><span foreground=\"green\"><b>Bienvenido:\n</b></span></big></big></big> %s" %name)
			self.label_name.set_use_markup(gtk.TRUE)
		else:
			self.label_name.set_markup("<big><big><big><span foreground=\"red\"><b>Acceso Denegado\n</b></span></big></big></big>")
		self.label_name.show()
		delay = gobject.timeout_add(2000,self.do_nothing)

	# método para borrar el mensaje de bienvenida o denegación de acceso
	def do_nothing(self):
		self.label_name.hide()
		return gtk.FALSE

	# método para avanzar el reloj en pantalla
	def display_current_time(self, widget, data=None):
		big ="<big><big><big><big><big><big><big><big><big><big> %s \
		</big></big></big></big></big></big></big></big></big></big>"
		# mostrar cadena big con funcion para obtener tiempo
		widget.set_markup(big % time.strftime("%H:%M:%S"))
		widget.set_use_markup(gtk.TRUE)	# uso de marcas especiales para formato de texto
		return gtk.TRUE
	
	# rutina para leer el buffer de arduino cada 1000ms (1s)
	def read_id(self):
		try:
			if self.arduino.isOpen():
				self.string = self.arduino.readline()
				print "Lector:",self.string
				if self.string == '':
					pass
				else:
					#self.entry.set_text(string)
					self.callback_code()
			else:
				self.arduino.close()
				del self.arduino 
				print "lero lero"
				self.connection_routine()

		# si no hay instancia del arduino (self.arduino) se lanza la excepción
		# AttributeError y se muestra la alerta en interfaz de no hay arduino conectado
		# y se llama la rutina de conexión
		except AttributeError:
			print "Exodo del dialogo: ", self.warning_flag
			if self.warning_flag == False:
				self.create_warning_lector()
			print "Error: Access Lector not plugged"
			self.statusbar_push_item(self.error_status_bar, """Error: Dispositivo lector no detectado""")
			self.connection_routine()
			
		# si el puerto serial ya se había abierto y se perdió la conexión
		# se lanza la excepción SerialException, se cerrará el puerto y se
		# llama a la rutina de conexión
		except serial.serialutil.SerialException:
			print "Error: Access Lector unplugged"
			# mostrar dialogo de advertencia
			if self.warning_flag == False:
				self.create_warning_lector()
			self.arduino.close()
			# se elimina la variable self.arduino
			del self.arduino
			self.connection_routine()

		# se retorna valor verdadero para que se llame a esta rutina de nuevo
		return gtk.TRUE

	# método principal de la interfaz
	def main(self):
		gtk.main()	# se entrega el control a la interfaz gtk
