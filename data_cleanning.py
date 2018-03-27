# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 09:40:05 2017

@author: Yabra Muvdi
"""

import pandas as pd
import numpy as np
import string
import time

frames = []

for letra in list(string.ascii_uppercase):  
    try:
        nombre_archivo = "Genealogias_" + str(letra) + ".xlsx"
        excel = pd.ExcelFile(nombre_archivo)
    except:
        continue
    
    sheet = excel.sheet_names[0]
    df = excel.parse(sheet)
    df = df.replace(np.nan, '', regex=True)
    frames.append(df)

#Junto todos los datos
df = pd.concat(frames, axis=0, ignore_index=True)
df = df.replace(np.nan, '', regex=True)

#Encuentro la última columna y el espacio donde están las columnas con hijos
ultima_columna = df.shape[1]
num_col_hijos = (ultima_columna - 1) - df.columns.get_loc("Tipo Error")

#Arreglo los nombres de las columnas
for i in range(1, num_col_hijos + 1):
    nombre_col = "Hijo_" + str(i)
    nombre_reemplazar = "Unnamed: " + str(df.columns.get_loc("Tipo Error") + i)
    df = df.rename(columns = {nombre_reemplazar:nombre_col})
    nombre_col = "ID_" + nombre_col
    df[nombre_col] = None

#Creo las columnas con todos los tipos de ID´s que voy a tener
df["ID"] = None
df["ID_Padre"] = None
df["ID_Madre"] = None
df["ID_Conyugue"] = None
df["Hijos_Encontrados"] = 0


#Extraigo las observaciones con error para corregirlas
df = df.rename(columns = {"Tipo Error":"Tipo_Error"})
df_errores = df[df.Tipo_Error != ""]
lista_url_errores = df_errores.Link
lista_url_errores = lista_url_errores.tolist()

#Borro las observaciones que presentaron error
df = df[df.Tipo_Error == ""]
ultima_fila = df.shape[0] 
df = df.reset_index(drop = True)

#Genero una cuenta para el número de hijos de cada persona
df["Cantidad_Hijos"] = 0

inicio = time.time()
for n in range(ultima_fila):
    num_hijos = 0
    for i in range(1, num_col_hijos):
        col_hijo = "Hijo_" + str(i)
        if df.iloc[n][col_hijo] != "":
            num_hijos += 1
    df.loc[n]["Cantidad_Hijos"] = num_hijos

print("El loop que calcula la cantidad de hijos tarda: " + str((time.time() - inicio)/60) + " minutos")

#Declaro como número enteros a FAM_C y FAM_S
df[["Fam_C", "Fam_S"]].apply(pd.to_numeric)

#Genero un ID único que corresponda con el orden de la base
df["ID"] = df.index + 1

#Genero las variables quue van a contener el ID de los hijos
inicio = time.time()
for v in range (1, num_col_hijos):
    nombre = "ID_Hijo_" + str(v)
    df[nombre] = None
duracion = (time.time() - inicio)/60
print("La creación de 30 variables vacias demoró : " + str(duracion) + " minutos") 

#Cambio el género por una Dummy
df["Genero"] = (df["Genero"] == "Femenino").astype(int)

#Guardo el DataFrame en Excel
writer = pd.ExcelWriter("base_final.xlsx", options={'strings_to_urls': False})
df.to_excel(writer, "Sheet1")
writer.save()
