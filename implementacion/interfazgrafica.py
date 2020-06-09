#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import scrolledtext
from lectura import Articulo
from lectura import PageRank


class Aplicacion():
    OptionList = [ "Todos los campos", "Titulo", "Abstract", "Palabras clave"]

    def __init__(self):
        self.pagerank = PageRank()

        self.AutorList = list(self.pagerank.autores)

        self.raiz = Tk()
        self.raiz.geometry('550x300')

        self.raiz.title('Buscador')

        self.tinfo = scrolledtext.ScrolledText(self.raiz, width=40, height=10)
        self.tinfo.grid(column = 0, row = 6)

        self.tentry = Entry(self.raiz, width=40)
        self.tentry.grid(column = 0, row = 5)

        self.binfo = ttk.Button(self.raiz, text='Buscar',                      command=self.verinfo)
        self.binfo.grid(column = 1, row =5)

        self.bper = ttk.Button(self.raiz, text='Busqueda personalizada',        command=self.verper)
        self.bper.grid(column = 1, row =3)


        self.bsalir = ttk.Button(self.raiz, text='Salir',
                                 command=self.raiz.destroy)
        self.bsalir.grid(column = 2, row = 5)

        self.variable = tk.StringVar(self.raiz)
        self.variable.set(self.OptionList[0])
        opt = tk.OptionMenu(self.raiz, self.variable, *self.OptionList)
        opt.config(width=30, font=('Helvetica', 12))
        opt.grid(column = 0, row = 1)

        self.variable2 = tk.StringVar(self.raiz)

        self.variable2.set(self.AutorList[0])
        opt2 = tk.OptionMenu(self.raiz, self.variable2, *self.AutorList)
        opt2.config(width=30, font=('Helvetica', 12))
        opt2.grid(column = 0, row = 3)

        self.labelTest = tk.Label(text="", font=('Helvetica', 12), fg='red')
        self.labelTest.grid(column = 0, row = 2)
        self.variable.trace("w", self.callback)

        self.labelTest2 = tk.Label(text="", font=('Helvetica', 12), fg='red')
        self.labelTest2.grid(column = 0, row = 4)
        self.variable2.trace("w", self.callback2)

        self.tentry.focus_set()
        self.raiz.mainloop()

    def callback(self, *args):
        self.labelTest.configure(text="Has seleccionado {}".format(self.variable.get()))

    def callback2(self, *args):
        self.labelTest2.configure(text="Has seleccionado {}".format(self.variable2.get()))

    def verinfo(self):

        self.tinfo.delete("1.0", END)

        palabra = self.tentry.get()

        res = self.pagerank.filtrar(palabra, self.variable.get())
        texto_info = ""
        if(not res):
            texto_info = "No hay articulos que coincidan con su búsqueda \n"
        else:
            if(isinstance(res, list)):
                for r in res:
                    texto_info += r.titulo + "\n"
            else:
                texto_info = res

        self.tinfo.insert("1.0", texto_info)

    def verper(self):

            self.tinfo.delete("1.0", END)
            palabra = self.tentry.get()

            res = self.pagerank.busquedapersonalizada(palabra)
            texto_info = ""
            if(not res):
                texto_info = "No hay articulos que coincidan con su búsqueda \n"
            else:
                if(isinstance(res, list)):
                    for r in res:
                        texto_info += r.titulo + "\n"
                else:
                    texto_info = res

            self.tinfo.insert("1.0", texto_info)

def main():
    mi_app = Aplicacion()
    return 0


main()
