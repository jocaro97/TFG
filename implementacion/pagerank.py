import xml.dom.minidom
import os
import re
import numpy as np
from time import time
import os.path
import math
import csv

# Constantes globales.
C = 0.85
NUM_TERMINOS = 25

# Rutas.
PATH = "/home/johanna/Documentos/TFG/implementacion/matrices/"
BBDPATH = "/home/johanna/Documentos/TFG/base-de-datos/base"

# Clase que recoge toda la información de un documento del conjunto de datos
# PMSC-UGR. En un objeto de la clase artículo se guarda:
# Título, palabras_titulo (guarda en una lista las palabras del título), pmid,
# abstract, palabras_abstract (guarda en una lista las palabras del abstract),
# keywords, autores (lista con los autores), citasAutor (ORCID de los autores
# citados), citasPmid (pmid de los documentos citados).
class Articulo:
    def __init__(self, ruta):
        doc = xml.dom.minidom.parse(ruta)
        pmids = doc.getElementsByTagName("ARTICLE-PMID")
        for pmid in pmids:
            self.pmid = pmid.firstChild.nodeValue

        titulos = doc.getElementsByTagName("ARTICLE-TITLE")
        self.palabras_titulo = []
        for titulo in titulos:
            tit = titulo.firstChild.nodeValue
            self.titulo = tit
            tit = re.split('(\W)', tit)
            for t in tit:
                if(t == ' ' or t == ''):
                    tit.remove(t)
            self.palabras_titulo = np.array(tit)


        abstract = doc.getElementsByTagName("ARTICLE-ABSTRACT")
        self.abstract =[]
        self.palabras_abstract = []
        for abs in abstract:
            if abs.firstChild:
                abstract = abs.firstChild.nodeValue
                self.abstract.append(abstract)
                abstract = re.split('(\W)', abstract)
                for a in abstract:
                    if(a == ' ' or a == ''):
                        abstract.remove(a)
                self.palabras_abstract = np.array(abstract)


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
                keywords = word.firstChild.nodeValue.split(',')
                self.keywords.append(keywords)

        self.keywords = np.array(self.keywords)

# Clase que implementa el algoritmo PageRank y dos modelos del ámbito de la
# Recuperación de Información (modelo booleano y modelo vectorial).
class PageRank:
    m = 0
    v = 0
    def __init__(self):
        print("Carganco la base de datos\n")
        # Si existen los archivos preprocesados se utilizan estos.
        if(os.path.exists(PATH + "vectorPG.csv")):
            start = time()
            archivos = self.devolverArchivos(BBDPATH)
            self.pg = []
            with open(PATH + 'vectorPG.csv') as file:
                reader = csv.reader(file)
                for row in reader:
                    self.pg.append(float(row[0]))
            start = time()

            self.nodos = []
            self.autores = set()
            self.palabras = set()
            for archivo in archivos:
                a = Articulo(archivo)

                self.nodos.append(a)
                for autor in a.autores:
                    self.autores.add(autor)

                if a.keywords.size:
                    for palabra in a.keywords[0]:
                        self.palabras.add(palabra)

                for abstract in a.palabras_abstract:
                    self.palabras.add(abstract)

                for tit in a.palabras_titulo:
                    self.palabras.add(tit)


            self.palabras = list(self.palabras)
            self.palabras.sort()

            self.v, _ = self.ordenar(self.nodos.copy(),self.pg.copy())

            self.w = np.loadtxt(PATH + 'matrizw.csv', dtype=np.float, delimiter=',', skiprows = 0)

            self.t = np.loadtxt(PATH + 'matrizt.csv', dtype=np.float, delimiter=',', skiprows = 0)
            elapsed_time = time() - start
            print("Tiempo que tarda en cargar el conjunto de datos: ", elapsed_time)

        # Si no existen los archivos, se crean.
        else:
            start = time()
            archivos = self.devolverArchivos(BBDPATH)

            self.nodos = []
            self.autores = set()
            self.palabras = set()
            for archivo in archivos:
                a = Articulo(archivo)

                self.nodos.append(a)
                for autor in a.autores:
                    self.autores.add(autor)

                if a.keywords.size:
                    for palabra in a.keywords[0]:
                        self.palabras.add(palabra)

                for abstract in a.palabras_abstract:
                    self.palabras.add(abstract)

                for tit in a.palabras_titulo:
                    self.palabras.add(tit)

            elapsed_time = time() - start
            print("Tiempo que tarda en cargar el conjunto de datos: ", elapsed_time)
            self.palabras = list(self.palabras)
            self.palabras.sort()

            start = time()
            self.v = self.construirmatriz(self.nodos.copy())
            elapsed_time = time() - start
            print("El tiempo en construir la matriz es: ", elapsed_time)
            self.calculamatrices()
            print("Terminado")

    # Función que devuelve todos los archivos PMSC-UGR de un directorio.
    def devolverArchivos(self, carpeta):
        archivos = []
        for archivo in os.listdir(carpeta):
            if(re.match('PMSC-UGR-[0-9]*.xml', archivo)):
                archivos.append(os.path.join(carpeta,archivo))

        return archivos

    # Método de las potencias, utilizado para aproximar el vector de Perron.
    def metodopotencias(self, m, num_iterations=100):
        N = m.shape[1]

        v = np.random.rand(N, 1)
        v = v / np.linalg.norm(v, 1)

        for i in range(num_iterations):
            v = m @ v

        return v

    # Método que ordena una lista de documentos por su peso.
    def ordenar(self, vector, valores, borrarceros = False):
        res = []
        ranking = []
        for i in range(len(self.nodos)):
            indice = valores.index(max(valores))
            if(borrarceros):
                if(max(valores) > 0.0):
                    res.append(vector[indice])
                    ranking.append(max(valores))
            else:
                res.append(vector[indice])
                ranking.append(max(valores))

            valores.pop(indice)
            vector.pop(indice)

        return res, ranking

    # Método que devuelve una lista con todos los pmids de los objetos artículo.
    def listapmid(self, v):
        pmids = []
        for articulo in v:
            pmids.append(articulo.pmid)

        pmids = np.array(pmids)
        return pmids

    # Método que construye la matriz de adyacencia para el algoritmo PageRank.
    def construirmatriz(self, v):
        m = np.zeros((len(v),len(v)))
        pmids = self.listapmid(v)

        for articulo in v:
            for cita in articulo.citasPmid:
                index = np.where(pmids == cita)
                m[index, v.index(articulo)] += 1


        if m.any() != 0:
            for i in range(len(v)):
                if sum(m.T[i]) != 0:
                    m.T[i] = m.T[i] / sum(m.T[i])

        self.m = m

        N = m.shape[1]
        m_seg = (C * m + (1 - C)/N)
        resultado = self.metodopotencias(m_seg)

        self.pg = resultado.flatten()
        resultado = resultado.tolist()

        with open(PATH + 'vectorPG.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(resultado)

        v, _ = self.ordenar(v,resultado)

        return v

    # Método que calcula la matriz de frecuencias y la matriz de pesos.
    def calculamatrices(self):
        t = np.zeros((len(self.nodos), len(self.palabras)))
        nodos = np.array(self.nodos)
        palabras = np.array(self.palabras)

        for i in range(len(t)):
            for j in range(len(t[i])):
                if nodos[i].keywords.size:
                    index = np.where(nodos[i].keywords[0] == palabras[j])
                    t[i,j] += len(index[0])
                index = np.where(nodos[i].palabras_abstract == palabras[j])
                t[i,j] += len(index[0])
                index = np.where(nodos[i].palabras_titulo == palabras[j])
                t[i,j] += len(index[0])

        self.t = t

        with open(PATH + 'matrizt.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(t)

        n = self.t > 0
        n = n.astype(np.int)
        w = np.zeros((len(self.nodos), len(self.palabras)))
        for i in range(len(w)):
            for j in range(len(w[i])):
                w[i,j] = self.t[i,j] * math.log((len(self.nodos))/ sum(n[:,j]))

        for i in range(len(w)):
            w[i] = w[i] / np.linalg.norm(w[i])

        self.w = w
        with open(PATH + 'matrizw.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(w)

    # Función de búsqueda para el modelo booleano.
    # Dada una palabra o término y una lista de documentos, el método devuelve
    # un subconjunto formado por los documentos que contienen la palabra o
    # término.
    def buscar(self, palabra, sitio, v):
        res = set()
        if(sitio == "Abstract" or sitio == "Todos los campos"):
            for i in range(len(v)):
                if v[i].abstract:
                    if(re.findall(palabra, v[i].abstract[0])):
                        res.add(v[i])

        if(sitio == "Título" or sitio == "Todos los campos"):
            for i in range(len(v)):
                if v[i].titulo:
                    if(re.findall(palabra, v[i].titulo)):
                        res.add(v[i])

        if(sitio == "Palabras clave" or sitio == "Todos los campos"):
            for i in range(len(v)):
                if v[i].keywords.size:
                    for word in v[i].keywords[0]:
                        if(re.findall(palabra, word)):
                            res.add(v[i])
        return list(res)

    # Función utilizada en el modelo booleano. Detecta las
    # estructuras lógicas y devuelve una lista con el resultado
    def calcular(self, sentencia, resultados, sitio):
        i = 0
        if(sentencia[0] == "("):
            sentencia.pop(0)
            resultados.pop(0)

        if(sentencia[len(sentencia)-1] == ")"):
            sentencia.pop(len(sentencia)-1)

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

        return resultados[0]

    # Ordena una lista de documentos por el PageRank. Se utiliza en el modelo
    # booleano.
    def ordenarresultados(self, resultados):
        res = []
        ranking = []
        for a in self.v :
            for r in resultados:
                if(r == a):
                    res.append(r)
                    ranking.append(self.pg[self.nodos.index(a)])

        return res, ranking

    # Función principal de búsqueda en el modelo booleano.
    def filtrar(self, texto, sitio):
        ranking = 0
        texto = re.split('(\W)', texto)

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
                        return res, ranking
                i += 1


        for i in texto:
            if(i == ' '):
                texto.remove(i)

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
                        return "Error en el operador lógico", ranking
                    texto[ind_start] = "SeNtenCia"
                    resultados[ind_start] = res
                    for j in range(ind_start+1, i+1):
                        texto.pop(ind_start +1)
                        resultados.pop(ind_start + 1)
                    i = 0
                else:
                    res = "Error no se encontró ( de abrir"
                    print(res)
                    return res, ranking
            else:
                i += 1

        if(copiar):
            print("Error no se encontró ) de cerrar")
            res = "Error no se encontró ) de cerrar"
        else:
            res = self.calcular(texto, resultados, sitio)
            if(res != "Error en el operador lógico."):
                res, ranking = self.ordenarresultados(res)

        return res, ranking

    # Búsqueda del modelo vectorial.
    def busquedapersonalizada(self,texto, autor, personalizada):
        ranking = 0
        texto = re.split('(\W)', texto)
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

        t_q = np.zeros(len(self.palabras))
        nodos = np.array(self.nodos)
        palabras = np.array(self.palabras)
        texto = np.array(texto)
        n = self.t > 0
        n = n.astype(np.int)
        for j in range(len(t_q)):
            index = np.where(texto == palabras[j])
            t_q[j] = len(index[0])

        q = np.zeros(len(self.palabras))
        for i in range(len(q)):
            q[i] = t_q[i] * math.log((len(self.nodos))/ sum(n[:,i]))


        q = q / np.linalg.norm(q)

        # Si es personalizada se utiliza la función de Rocchio
        if(personalizada):

            relevantes = []
            for n in nodos:
                for a in n.autores:
                    if(a == autor):
                        indices, = np.where(nodos == n)
                        relevantes.append(indices[0])


            aux = np.zeros(len(self.palabras))
            for i in relevantes:
                aux += 0.75 * self.w[i] / (len(relevantes))

            rocchio = q + aux
            q_prima = np.zeros(len(self.palabras))
            for i in range(NUM_TERMINOS):
                q_prima[np.argmax(rocchio)] = np.max(rocchio)
                rocchio[np.argmax(rocchio)] = -1

            sim = np.zeros(len(self.nodos))
            for i in range(len(sim)):
                sim[i] = sum(q_prima * self.w[i]) / (np.linalg.norm(self.w[i]) * np.linalg.norm(q_prima))
        else:
            sim = np.zeros(len(self.nodos))
            for i in range(len(sim)):
                sim[i] = sum(q * self.w[i]) / (np.linalg.norm(self.w[i]) * np.linalg.norm(q))

        res = np.array(self.pg) * sim
        res = res.tolist()
        res, ranking = self.ordenar(self.nodos.copy(), res, True)

        return res, ranking



def main():
    pg = PageRank()
