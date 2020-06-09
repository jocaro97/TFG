import xml.dom.minidom
import os
import re
import numpy as np
from time import time
import os.path
import math

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
                self.keywords.append(word.firstChild.nodeValue.split(','))

        self.keywords = np.array(self.keywords)


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
            self.nodos = []
            self.autores = set()
            self.palabras = set()
            for archivo in archivos:
                a = Articulo(archivo)
                self.nodos.append(a)
                for autor in a.autores:
                    self.autores.add(autor)

                for palabra in a.keywords[0]:
                    self.palabras.add(palabra)
            elapsed_time = time() - start
            print("Tiempo que tarda en cargar la base de datos: ", elapsed_time)

            resultado = self.metodopotencias(self.m)
            resultado = resultado.tolist()
            self.v = self.ordenar(self.nodos.copy(),resultado)
            print(self.autores)
            self.palabras = list(self.palabras)
            print(self.palabras)
            for articulo in self.v:
                print(articulo.titulo)
                print(articulo.abstract)
                print(articulo.keywords)

            self.calcularmatrizfrecuencias()


        else:
            start = time()
            #archivos = devolverArchivos("/home/johanna/Documentos/TFG/base-de-datos/PMSC-UGR-XML")
            archivos = self.devolverArchivos("/home/johanna/Documentos/TFG/implementacion/prueba")
            self.nodos = []
            for archivo in archivos:
                self.nodos.append(Articulo(archivo))
            elapsed_time = time() - start
            print("Tiempo que tarda en cargar la base de datos: ", elapsed_time)
            start = time()
            self.v = self.construirmatriz(self.nodos)
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

    def calcularmatrizfrecuencias(self):
        t = np.zeros((len(self.nodos), len(self.palabras)))
        nodos = np.array(self.nodos)
        palabras = np.array(self.palabras)
        for i in range(len(t)):
            for j in range(len(t[i])):
                index = np.where(nodos[i].keywords[0] == palabras[j])
                t[i,j] = len(index[0])

        self.t = t

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
                    for word in v[i].keywords[0]:
                        if(re.findall(palabra, word)):
                            res.append(v[i])
        return res

    def calcular(self, sentencia, resultados, sitio):
        i = 0
        if(sentencia[0] == "("):
            sentencia.pop(0)
            resultados.pop(0)

        if(sentencia[len(sentencia)-1] == ")"):
            sentencia.pop(len(sentencia)-1)

        print(sentencia)
        while(len(sentencia) > 1):
            if(sentencia[0] == "NOT"):
                if(sentencia[1] != "SeNtenCia"):
                    primero = self.buscar(sentencia[1], sitio, resultados[1])
                else:
                    primero = resultados[1]

                primero = set(primero)
                aux = set(resultados[1])
                primero = aux - primero

                i = 1
            else:
                if(sentencia[0] != "SeNtenCia"):
                    primero = self.buscar(sentencia[0], sitio, resultados[0])
                else:
                    primero = resultados[0]

            if(len(sentencia) > 2+i):
                if(sentencia[2+i] == "NOT"):
                    if(sentencia[3+i] != "SeNtenCia"):
                        segundo = self.buscar(sentencia[3+i], sitio, resultados[3+i])
                    else:
                        segundo = resultados[3+i]
                    segundo = set(segundo)
                    aux = set(resultados[3+i])
                    segundo = aux - segundo
                    final = 3+i
                else:
                    if(sentencia[2+i] != "SeNtenCia"):
                        segundo = self.buscar(sentencia[2+i], sitio, resultados[2+i])
                    else:
                        segundo = resultados[2+i]
                    final = 2+i
            else:
                return "Error en el operador lógico."

            if(sentencia[1+i] == 'AND'):
                resultados[0] = [value for value in primero if value in segundo]
            elif(sentencia[1+i] == 'OR'):
                resultados[0] = primero + segundo
                resultados[0] = list(set(resultados[0]))
            else:
                return "Error en el operador lógico."


            sentencia[0] = "SeNtenCia"
            for j in range(0,final):
                sentencia.pop(1)
                resultados.pop(1)

            i = 0


        if(len(sentencia) == 1 and sentencia[0] != "SeNtenCia"):
            resultados[0] = self.buscar(sentencia[0], sitio, resultados[0])

        print(resultados[0])
        for i in range(len(resultados[0])):
            print(resultados[0][i].titulo)
        return resultados[0]

    def ordenarresultados(self, resultados):
        res = []
        for a in self.v :
            for r in resultados:
                if(r == a):
                    res.append(r)

        return res

    def filtrar(self, texto, sitio):
        texto = re.split('(\W)', texto)
        print(texto)
        i = 0
        while(i < len(texto)):
            if(texto[i] == ''):
                texto.pop(i)
            else:
                if(texto[i] == '"'):
                    primera_no = True
                    while(i+1 < len(texto) and texto[i+1] != '"'):
                        if(primera_no):
                            texto[i] = texto[i+1]
                            primera_no = False
                            texto.pop(i+1)
                        else:
                            texto[i] = texto[i] + texto[i+1]
                            texto.pop(i+1)

                    if(i+1 < len(texto)):
                        texto.pop(i+1)
                    else:
                        res = "Error no se encontro \" de cerrar."
                        print("Error no se encontro \" de cerrar.")
                        return res
                i += 1


        for i in texto:
            if(i == ' '):
                texto.remove(i)
        print(texto)
        resultados = []
        for j in range(len(texto)):
            resultados.append(self.v.copy())

        i = 0
        sentencia = []
        copiar = False
        while(i < len(texto)):
            if(texto[i] == '('):
                ind_start = i
                sentencia = []
                copiar = True

            if(copiar):
                sentencia.append(texto[i])

            if(texto[i] == ")"):
                if(copiar):
                    copiar = False
                    res = self.calcular(sentencia,  resultados[ind_start:i], sitio)
                    if(res == "Error en el operador lógico."):
                        return "Error en el operacor lógico"
                    texto[ind_start] = "SeNtenCia"
                    resultados[ind_start] = res
                    for j in range(ind_start+1, i+1):
                        texto.pop(ind_start +1)
                        resultados.pop(ind_start + 1)
                    i = 0
                else:
                    res = "Error no se encontro ( de abrir"
                    print(res)
                    return res
            else:
                i += 1

        if(copiar):
            print("Error no se encontro ) de cerrar")
            res = "Error no se encontro ) de cerrar"
        else:
            res = self.calcular(texto, resultados, sitio)
            if(res != "Error en el operador lógico."):
                res = self.ordenarresultados(res)

        return res

    def busquedapersonalizada(self,texto):
        texto = re.split('(\W)', texto)
        print(texto)
        i = 0
        while(i < len(texto)):
            if(texto[i] == ''):
                texto.pop(i)
            else:
                if(texto[i] == '"'):
                    primera_no = True
                    while(i+1 < len(texto) and texto[i+1] != '"'):
                        if(primera_no):
                            texto[i] = texto[i+1]
                            primera_no = False
                            texto.pop(i+1)
                        else:
                            texto[i] = texto[i] + texto[i+1]
                            texto.pop(i+1)

                    if(i+1 < len(texto)):
                        texto.pop(i+1)
                    else:
                        res = "Error no se encontro \" de cerrar."
                        print("Error no se encontro \" de cerrar.")
                        return res
                i += 1


        for i in texto:
            if(i == ' '):
                texto.remove(i)

        w = np.zeros((len(self.nodos)+1, len(self.palabras)))
        q = np.zeros(len(self.palabras))
        nodos = np.array(self.nodos)
        palabras = np.array(self.palabras)
        texto = np.array(texto)
        for j in range(len(q)):
            index = np.where(texto == palabras[j])
            q[j] = len(index[0])
        self.t = np.vstack((self.t, q))
        n = self.t > 0
        n = n.astype(np.int)
        for i in range(len(w)):
            for j in range(len(w[i])):
                w[i,j] = self.t[i,j] * math.log((len(self.nodos))/ sum(n[:,j]))


        for i in range(len(w)):
            w[i] = w[i] / np.linalg.norm(w[i])
            if( i < len(nodos)):
                print(nodos[i].titulo)
                print(w[i])

        print(w)

        return "Resultado"

def main():
    pg = PageRank()

main()
