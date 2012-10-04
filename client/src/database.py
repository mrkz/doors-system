#!/usr/bin/env python
#coding=utf-8
"""\\
Conexión a la base de datos local para comprobar acceso
Centro Universitario de Ciencias Exactas e Ingenierias."""

import string				# módulo para manejo de cadenas
import mysql.connector		# módulo para funciones de mysql

class Connection:

	def __init__(self, HOST = 'localhost', USER = 'system',
				 PASSWORD = 'password', DATABASE = 'cucei'):
		# Se crea la conexión a la base de datos
		self.connection = mysql.connector.Connect(host = HOST, user = USER,
												   password = PASSWORD, 
												   database = DATABASE)
		# se crea el cursor para ejecutar comandos
		self.cursor = self.connection.cursor()
	
	# método para insertar la tupla en la tabla recibida
	# table = "<nombre_tabla>", tupla = (<val>[,<val>])
	def insert_on_table(self, table = None, tuple = None):
		value = 0
		if (table and tuple):	# si recibio tabla y tupla
			value = self.cursor.execute("INSERT INTO %s VALUES %s" % (table, tuple))
		if value == -1:
			print "Tuple: %s inserted on %s" % (tuple, table)
			# se sincroniza a la base de datos
			self.connection.commit()
		else:
			print "Error: cannot insert tuple"

	# método para obtener (o denegar) acceso
	def get_access(self, code = None, door = None):

		flag = False			# acceso denegado por defecto
		code_lenght = len(code)
		if code_lenght == 7 or code_lenght == 9:
			value = self.cursor.execute("SELECT * FROM Acceso_puertas WHERE codigo=\"%s\" AND id_puerta=\"%s\"" % (code,door) )
			if value != -1:
				print "Error: cannot execute query"
			else:				# se ejecutó query exitosamente
				tuples = []		# se declara lista con las tuplas que se obtuvieron
				
				# formato de las tuplas en 'Acceso_puertas':
				# 		(id_puerta, codigo, permiso, status)
				# i.e.: ( 		 1, 1111111,	  1, 	  1)
				# tipos:(	   INT,		INT,BOOLEAN,	INT)
				# 
				# id_puerta: un identificador de una puerta válido
				# codigo:	 un código de alumno o maestro válido
				# permiso:	 1 si tiene permiso, 0 en caso contrario
				# status:	 1 si persona activa, 0 en caso contrario
				
				for row in self.cursor:	
					tuples.append(row)		# añadir la K-tupla a la lista
				
				if len(tuples) > 0:
					for i in tuples:
						# si tiene permiso
						if (i[2] == 1):
							if (i[3] == 1):		# si estatus es activo
								flag = True
							else:
								print "Forbidden: status inactivo"
						else:
							print "Forbidden: Sin permiso"
				else:		# no hay tuplas, por lo tanto, no hay permiso
					print "Forbidden: Sin permiso (",code,")"
		return flag

	def close(self):
		
		self.connection.close()
