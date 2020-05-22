import xml.dom.minidom
import os
import re
import numpy as np
from time import time
import os.path

# Constantes globales
C = 0.85

class Articulo:
    def __init__(self, ruta):
        doc = xml.dom.minidom.parse(ruta)
        pmids = doc.getElementsByTagName("ARTICLE-PMID")
        for pmid in pmids:
            self.pmid = pmid.firstChild.nodeValue

        titulos = doc.getElementsByTagName("ARTICLE-TITLE")
        for titulo in titulos:
            self.titulo = titulo.firstChild.nodeValue

        abstract = doc.getElementsByTagName("ARTICLE-ABSTRACT")
        self.abstract =[]
        for abs in abstract:
            if abs.firstChild:
                self.abstract.append(abs.firstChild.nodeValue)

        orcid = doc.getElementsByTagName("ORCID")

        self.autores = []
        for id in orcid:
            self.autores.append(id.firstChild.nodeValue)

        citaciones = doc.getElementsByTagName("CITATION")
        self.citasAutor = []
        for cita in citaciones:
            autores = cita.getElementsByTagName("CITATION-AUTHORS-ORCIDS")
            for autor in autores:
                self.citasAutor.append(autor.firstChild.nodeValue.split(', '))

        self.citasPmid = []
        for cita in citaciones:
            pmids = cita.getElementsByTagName("CITATION-PMID")
            for pmid in pmids:
                self.citasPmid.append(pmid.firstChild.nodeValue)

        keywords = doc.getElementsByTagName("ARTICLE-KEYWORDS")
        self.keywords = []
        for word in keywords:
            if word.firstChild:
                self.keywords.append(word.firstChild.nodeValue)


class PageRank:
    m = 0
    v = 0
    def __init__(self):
        print("Carganco la base de datos\n")
        if(os.path.exists("/home/johanna/Documentos/TFG/implementacion/matriz.npy")):
            self.m = np.load("/home/johanna/Documentos/TFG/implementacion/matriz.npy")
            start = time()
            #archivos = devolverArchivos("/home/johanna/Documentos/TFG/base-de-datos/PMSC-UGR-XML")
            archivos = self.devolverArchivos("/home/johanna/Documentos/TFG/implementacion/prueba")
            nodos = []
            for archivo in archivos:
                nodos.append(Articulo(archivo))
            elapsed_time = time() - start
            print("Tiempo que tarda en cargar la base de datos: ", elapsed_time)

            resultado = self.metodopotencias(self.m)
            resultado = resultado.tolist()
            self.v = self.ordenar(nodos,resultado)
            for articulo in self.v:
                print(articulo.titulo)
                print(articulo.abstract)
                print(articulo.keywords)


        else:
            start = time()
            #archivos = devolverArchivos("/home/johanna/Documentos/TFG/base-de-datos/PMSC-UGR-XML")
            archivos = self.devolverArchivos("/home/johanna/Documentos/TFG/implementacion/prueba")
            nodos = []
            for archivo in archivos:
                nodos.append(Articulo(archivo))
            elapsed_time = time() - start
            print("Tiempo que tarda en cargar la base de datos: ", elapsed_time)
            start = time()
            self.v = self.construirmatriz(nodos)
            elapsed_time = time() - start
            print("El tiempo en construir la matriz es: ", elapsed_time)


    def devolverArchivos(self, carpeta):
        archivos = []
        for archivo in os.listdir(carpeta):
            if(re.match('PMSC-UGR-[0-9]*.xml', archivo)):
                archivos.append(os.path.join(carpeta,archivo))

        return archivos

    def metodopotencias(self, m, num_iterations=100):
        N = m.shape[1]
        # Añadimos el porcentaje de "aburrimiento"
        m_seg = (C * m + (1 - C)/N)

        v = np.random.rand(N, 1)
        v = v / np.linalg.norm(v, 1)

        for i in range(num_iterations):
            v = m_seg @ v



        return v

    def ordenar(self, vector, valores, reverse = False):
        res = []
        for i in range(len(vector)):
            if(reverse):
                indice = valores.index(min(valores))
            else:
                indice = valores.index(max(valores))

            res.append(vector[indice])
            valores.pop(indice)
            vector.pop(indice)

        return res

    def listapmid(self, v):
        pmids = []
        for articulo in v:
            pmids.append(articulo.pmid)

        pmids = np.array(pmids)
        return pmids

    def construirmatriz(self, v):
        m = np.zeros((len(v),len(v)))
        pmids = self.listapmid(v)
        #for articulo in v:
        #    for citas in articulo.citasAutor:
        #        for cita in citas:
        #            for art in aux:
        #                for autor in art.autores:
        #                    if(cita == autor):
        #                        m[aux.index(art), v.index(articulo)] += 1

        #for articulo in v:
        #    for citas in articulo.citasPmid:
        #        for cita in citas:
        #            for art in aux:
        #                for pmid in art.pmid:
        #                    if(cita == pmid):
        #                        m[aux.index(art), v.index(articulo)] += 1

        i = 1
        for articulo in v:
            print(i)
            i += 1
            for citas in articulo.citasPmid:
                for cita in citas:
                    index = np.where(pmids == cita)
                    m[index, v.index(articulo)] += 1


        if m.any() != 0:
            for i in range(len(v)):
                if sum(m.T[i]) != 0:
                    m.T[i] = m.T[i] / sum(m.T[i])

        self.m = m
        np.save("/home/johanna/Documentos/TFG/implementacion/matriz", m)
        np.save("/home/johanna/Documentos/TFG/implementacion/v", v)
        print(m)
        resultado = self.metodopotencias(m)

        print(resultado)

        resultado = resultado.tolist()

        v = self.ordenar(v,resultado)
        for articulo in v:
            print(articulo.pmid)

        return v

    def buscar(self, palabra, sitio, v):
        res = []
        if(sitio == "Abstract" or sitio == "Todos los campos"):
            for i in range(len(v)):
                if v[i].abstract:
                    if(re.findall(palabra, v[i].abstract[0])):
                        res.append(v[i])

        if(sitio == "Titulo" or sitio == "Todos los campos"):
            for i in range(len(v)):
                if v[i].titulo:
                    if(re.findall(palabra, v[i].titulo[0])):
                        res.append(v[i])

        if(sitio == "Palabras clave" or sitio == "Todos los campos"):
            for i in range(len(v)):
                if v[i].keywords:
                    if(re.findall(palabra, v[i].keywords[0])):
                        res.append(v[i])
        return res

    def filtrar(self, texto, sitio):
        texto = re.split('(\W)', texto)
        print(texto)
        i = 0
        while(i < len(texto)):
            if(texto[i] == ''):
                texto.remove(texto[i])
            else:
                if(texto[i] == '"'):
                    while(i+1 < len(texto) and texto[i+1] != '"'):
                        print(texto[i])
                        texto[i] = texto[i] + texto[i+1]
                        texto.remove(texto[i+1])

                    if(i+1 < len(texto)):
                        texto[i] = texto[i] + texto[i+1]
                        texto.remove(texto[i+1])
                    else:
                        print("Error no se encontro \" de cerrar")
                i += 1

        for i in texto:
            if(i == ' '):
                texto.remove(i)
        print(texto)
        palabras = texto
        res = self.v
        for palabra in palabras:
            if((palabra != '(') and (palabra != ")")):
                print(palabra)
                res = self.buscar(palabra, sitio, res)

        return res

def main():
    pg = PageRank()

main()