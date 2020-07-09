#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import scrolledtext
from pagerank import Articulo
from pagerank import PageRank

# Interfaz gráfica
class Aplicacion():
    OptionList = [ "Todos los campos", "Título", "Abstract", "Palabras clave"]
    OptionMod = ["Vectorial", "Booleano"]
    OptionRank = ["No mostrar Ranking", "Mostrar Ranking"]

    def __init__(self):
        self.pagerank = PageRank()
        self.ranking = None
        self.res = None

        lista = list(self.pagerank.autores)
        lista.sort()
        self.AutorList = lista

        self.raiz = Tk()
        self.raiz.geometry('950x500')

        self.raiz.title('Buscador')

        # Celda donde se muestran los resultados.
        self.tinfo = scrolledtext.ScrolledText(self.raiz, width=50, height=30)
        self.tinfo.grid(column = 0, row = 6)

        # Celda donde se introduce la búsqueda.
        self.tentry = Entry(self.raiz, width=40)
        self.tentry.grid(column = 0, row = 5)

        # Botón de buscar.
        self.binfo = ttk.Button(self.raiz, text='Buscar',                      command=self.verinfo)
        self.binfo.grid(column = 1, row =5)

        # Botón de búsqueda personalizada.
        self.bper = ttk.Button(self.raiz, text='Búsqueda personalizada',        command=self.verper)
        self.bper.grid(column = 1, row =3)

        # Botón de mostrar Ranking inicial.
        self.bpag = ttk.Button(self.raiz, text='Mostrar Ranking inicial',        command=self.verpag)
        self.bpag.grid(column = 2, row =3)

        # Botón de salir.
        self.bsalir = ttk.Button(self.raiz, text='Salir',
                                 command=self.raiz.destroy)
        self.bsalir.grid(column = 2, row = 5)

        # Desplegable para elegir el sitio de búsqueda.
        self.variable = tk.StringVar(self.raiz)
        self.variable.set(self.OptionList[0])
        opt = tk.OptionMenu(self.raiz, self.variable, *self.OptionList)
        opt.config(width=30, font=('Helvetica', 12))
        opt.grid(column = 0, row = 1)

        # Desplegable para elegir el autor.
        self.variable2 = tk.StringVar(self.raiz)
        self.variable2.set(self.AutorList[0])
        opt2 = ttk.Combobox(self.raiz, textvariable = self.variable2, values = self.AutorList)
        opt2.config(width=30, font=('Helvetica', 12))
        opt2.grid(column = 0, row = 3)

        # Desplegable para elegir el modelo.
        self.variable3 = tk.StringVar(self.raiz)
        self.variable3.set(self.OptionMod[0])
        opt3 = tk.OptionMenu(self.raiz, self.variable3, *self.OptionMod)
        opt3.config(width=30, font=('Helvetica', 12))
        opt3.grid(column = 2, row = 1)

        # Desplegable para elegir si mostrar los pesos.
        self.variable4 = tk.StringVar(self.raiz)
        self.variable4.set(self.OptionRank[0])
        opt3 = tk.OptionMenu(self.raiz, self.variable4, *self.OptionRank)
        opt3.config(width=30, font=('Helvetica', 12))
        opt3.grid(column = 1, row = 1)

        # Muestra la opción del desplegable del sitio de búsqueda.
        self.labelTest = tk.Label(text="", font=('Helvetica', 12), fg='red')
        self.labelTest.grid(column = 0, row = 2)
        self.variable.trace("w", self.callback)

        # Muestra la opción del desplegable del autor.
        self.labelTest2 = tk.Label(text="", font=('Helvetica', 12), fg='red')
        self.labelTest2.grid(column = 0, row = 4)
        self.variable2.trace("w", self.callback2)

        # Muestra la opción del desplegable del modelo.
        self.labelTest3 = tk.Label(text="", font=('Helvetica', 12), fg='red')
        self.labelTest3.grid(column = 2, row = 2)
        self.variable3.trace("w", self.callback3)

        # Muestra la opción elegida de mostrar los pesos.
        self.labelTest4 = tk.Label(text="", font=('Helvetica', 12), fg='red')
        self.labelTest4.grid(column = 1, row = 2)
        self.variable4.trace("w", self.callback4)

        self.tentry.focus_set()
        self.raiz.mainloop()

    # Función que cambia el desplegable, cambia el sitio de búsqueda.
    def callback(self, *args):
        self.labelTest.configure(text="Has seleccionado {}".format(self.variable.get()))

    # Función que cambia el desplegable, cambia el autor.
    def callback2(self, *args):
        self.labelTest2.configure(text="Has seleccionado {}".format(self.variable2.get()))

    # Función que cambia el desplegable, cambia el modelo.
    def callback3(self, *args):
        self.labelTest3.configure(text="Has seleccionado {}".format(self.variable3.get()))

    # Función que cambia el desplegable, cambia la elección de mostrar los pesos.
    def callback4(self, *args):
        self.labelTest4.configure(text="Has seleccionado {}".format(self.variable4.get()))

        self.tinfo.delete("1.0", END)
        texto_info = ""
        if(not self.res):
            texto_info = "No hay articulos que coincidan con su búsqueda \n"
        else:
            if(isinstance(self.res, list)):
                if(self.variable4.get() == "No mostrar Ranking"):
                    for r in self.res:
                        texto_info += "- " + r.titulo + "\n"
                else:
                    for i in range(len(self.res)):
                        texto_info += "- " + self.res[i].titulo + " - "+ str(self.ranking[i]) +"\n"
            else:
                texto_info = self.res

        self.tinfo.insert("1.0", texto_info)


    # Función llamada por el boton "Buscar". Realiza la búsqueda de la consulta
    # introducida en el modelo fijado.
    def verinfo(self):

        self.tinfo.delete("1.0", END)

        palabra = self.tentry.get()

        if(self.variable3.get() == "Vectorial"):
            self.res, self.ranking = self.pagerank.busquedapersonalizada(palabra, self.variable2.get(), False)
        else:
            self.res, self.ranking = self.pagerank.filtrar(palabra, self.variable.get())
        texto_info = ""
        if(not self.res):
            texto_info = "No hay articulos que coincidan con su búsqueda \n"
        else:
            if(isinstance(self.res, list)):
                if(self.variable4.get() == "No mostrar Ranking"):
                    for r in self.res:
                        texto_info += "- " + r.titulo + "\n"
                else:
                    for i in range(len(self.res)):
                        texto_info += "- " + self.res[i].titulo + " - "+ str(self.ranking[i]) +"\n"
            else:
                texto_info = self.res

        self.tinfo.insert("1.0", texto_info)

    # Función llamada por el boton "Búsqueda personalizada". Realiza la búsqueda
    # de la consulta introducida con el método de realimentación de consultas.
    def verper(self):

            self.tinfo.delete("1.0", END)
            palabra = self.tentry.get()

            self.res, self.ranking = self.pagerank.busquedapersonalizada(palabra, self.variable2.get(), True)
            texto_info = ""
            if(not self.res):
                texto_info = "No hay articulos que coincidan con su búsqueda \n"
            else:
                if(isinstance(self.res, list)):
                    if(self.variable4.get() == "No mostrar Ranking"):
                        for r in self.res:
                            texto_info += "- " + r.titulo + "\n"
                    else:
                        for i in range(len(self.res)):
                            texto_info += "- " + self.res[i].titulo + " - "+ str(self.ranking[i]) +"\n"
                else:
                    texto_info = self.res

            self.tinfo.insert("1.0", texto_info)

    # Función llamada por el boton "Mostrar Ranking Inicial". Muestra
    # los documentos ordenados por el PageRank.
    def verpag(self):

            self.tinfo.delete("1.0", END)

            self.res, self.ranking = self.pagerank.ordenarresultados(self.pagerank.nodos.copy())
            texto_info = ""
            if(not self.res):
                texto_info = "No hay articulos que coincidan con su búsqueda \n"
            else:
                if(isinstance(self.res, list)):
                    if(self.variable4.get() == "No mostrar Ranking"):
                        for r in self.res:
                            texto_info += "- " + r.titulo + "\n"
                    else:
                        for i in range(len(self.res)):
                            texto_info += "- " + self.res[i].titulo + " - "+ str(self.ranking[i]) +"\n"
                else:
                    texto_info = self.res

            self.tinfo.insert("1.0", texto_info)


def main():
    mi_app = Aplicacion()
    return 0


main()
