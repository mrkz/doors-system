#!/usr/bin/env python
#coding=utf-8
"""\\
Ejecutando este script, se inicia la interfaz cliente
para el sistema de puertas.
Centro Universitario de Ciencias Exactas e Ingenierias."""

import string	# módulo para manejo de cadenas
import sys 		# módulo para manejo de directorios (importar módulos creados)

sys.path.append('./src')
sys.path.append('./GUI')

# se importan los módulos del programa
#
# form src.<module> import <class>
from GUI.window   import Window			# se importa clase para interfaz
from src.database import Connection		# se importa clase para DB

if __name__ == "__main__":
	window = Window()	# se hace instancia de la clase 'Window' (en GUI/window.py)
	window.main()

