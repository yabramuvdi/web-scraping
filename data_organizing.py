# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 21:18:12 2017

@author: Yabra Muvdi
"""

import pandas as pd
import numpy as np
import time

#Abro el archivo de Excel con la base completa
excel = pd.ExcelFile("base_final.xlsx")
sheet = excel.sheet_names[0]
df = excel.parse(sheet)
df = df.replace(np.nan, '', regex=True)

#Encuentro la última columna del arreglo de datos
ultima_fila = df.shape[0]

#Puedo empezar por reducir la base a solo las observaciones necesarias
df = df[["ID","Nombre", "Fam_C", "Fam_S", "Genero", "ID_Conyugue", "ID_Padre", "ID_Madre", "Hijos_Encontrados"]]

#Lleno los missings como 0
df["Fam_C"][df["Fam_C"] == ""] = 0
df["Fam_S"][df["Fam_S"] == ""] = 0

#Puedo empezar por hacer un sort
df = df.sort_values(by = "Fam_S")


#Itero a través de las personas para encontrar sus relaciones familiares
inicio = time.time()
for i in range(0, ultima_fila): 
    
    inicio_i = time.time()
    #Guardo el Fam_C y el Fam_S de la persona
    famc_i = df.iloc[i]["Fam_C"]
    fams_i = df.iloc[i]["Fam_S"]
      
    #Voy a revisar si la persona j tiene alguna relación con i
    for j in range(i + 1, ultima_fila):

        if famc_i == df.iloc[j]["Fam_S"]:
            
            if df.iloc[j]["Genero"] == 1:
                df.at[i, "ID_Madre"] = df.iloc[j]["ID"]
                nombre_id = "ID_Hijo_" + str(df.iloc[j]["Hijos_Encontrados"] + 1)
                df.at[j, nombre_id] = df.iloc[i]["ID"]
                df.at[j, "Hijos_Encontrados"] += 1
                continue
            
            elif df.iloc[j]["Genero"] == 0:
                df.at[i, "ID_Padre"] = df.iloc[j]["ID"]
                nombre_id = "ID_Hijo_" + str(df.iloc[j]["Hijos_Encontrados"] + 1)
                df.at[j, nombre_id] = df.iloc[i]["ID"]
                df.at[j, "Hijos_Encontrados"] += 1
                continue
        else: None

        if df.iloc[i]["Fam_S"] == df.iloc[j]["Fam_S"]:
            df.at[i, "ID_Conyugue"] = df.iloc[j]["ID"]
            df.at[j, "ID_Conyugue"] = df.iloc[i]["ID"]
            continue
        else: None
         
        if fams_i == df.iloc[j]["Fam_C"]:
            nombre_id = "ID_Hijo_" + str(df.iloc[i]["Hijos_Encontrados"] + 1)
            df.at[i, nombre_id] = df.iloc[j]["ID"]
            df.at[i, "Hijos_Encontrados"] += 1
            if df.iloc[i]["Genero"] == 0:
                df.at[j, "ID_Padre"] = df.iloc[i]["ID"]
            elif df.iloc[i]["Genero"] == 1:
                df.at[j, "ID_Madre"] = df.iloc[i]["ID"]
        else: None
    
    duracion_i = (time.time() - inicio_i)
    print("Acabó el loop de la persona " + str(i) + " que duró: " + str(duracion_i) + " segundos"  )

duracion = (time.time() - inicio)/60
print("El loop que encuenras los ID´s se demoró: " + str(duracion) + " minutos")

