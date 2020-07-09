# Método de ranking en el diseño de un sistema de acceso a la información

> Trabajo de Fin de Grado. Doble Grado en Ingeniería Informática y Matemáticas. Universidad de Granada

> Realizado por Johanna Capote Robayna y tutorizado por Silvia Acid Carrillo y Margarita Arias López


El objetivo de este trabajo es estudiar y entender el funcionamiento del algoritmo PageRank, además se implementa un buscador, cuya base es este algoritmo, que en respuesta a una consulta consiga recuperar información útil para el usuario dentro de una colección grande de documentos en los que podría estar potencialmente interesado.


La parte matemática se centra en el teorema de Perron-Frobenius para matrices no negativas. Este resultado permite determinar cuándo una matriz no negativa admite un valor propio dominante y constituye la base del algoritmo de PageRank. Se demuestra que el radio espectral de una matriz positiva es valor propio dominante y admite un vector propio con todas las entradas positivas (teorema de Perron) y se determina bajo qué condiciones se puede extender este resultado a matrices no negativas. Se estudia el comportamiento límite de las potencias de matrices con valor propio dominante y se justifica cómo este comportamiento permite aplicar un método iterativo, el conocido método de las potencias, para aproximar numéricamente el valor propio dominante y el llamado vector de Perron, cuando se trabaja con matrices de gran dimensión.

Para la parte de informática se ha implementado un buscador en lenguaje python, que consigue ordenar los archivos del conjunto de datos siguiendo el algoritmo PageRank. Adicionalmente se ha implementado una interfaz de usuario para facilitar la forma de introducir las consultas y mostrar los resultados de la búsqueda. Para poder realizar consultas en el sistema se han estudiado e implementado dos modelos diferentes, el modelo booleano y el modelo vectorial. Por último, con el objetivo de realizar consultas personalizadas se han estudiado e implementado la pseudo-realimentación de consulta, la cual extiende la consulta dependiendo de los documentos que le hayan resultado relevantes al usuario que realiza la consulta.


Palabras clave: PageRank, Perron-Frobenius, método de las potencias, Recuperación
de Información, buscador, modelo booleano, modelo vectorial, realimentación de consul-
tas.

## Texto

Para compilar el texto es necesario utilizar `lualatex`. 

## Código

El código se ha desarrollado con Python 3.7.6
