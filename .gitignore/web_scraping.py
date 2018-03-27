# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 19:16:15 2017

@author: Yabra Muvdi
"""

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import string
import xlsxwriter
from selenium.common.exceptions import TimeoutException

usuario_str = "yabra1995@gmail.com"
clave_str = "yabramuvdi95"


#Función para agregar información al Excel
def editar_excel(tabla, elementos, fila):

    for i in range(len(elementos)):
                
        #Información de padre y madre
        if (elementos[i].get_text() == "\xa0Padre" and len(elementos) >= (i + 2)):
            padre = elementos[i + 2].get_text()
            worksheet.write(fila, 13, padre)
            continue
        
        if elementos[i].get_text() == "\xa0Madre"and len(elementos) >= (i + 2):
            try:
                madre = elementos[i + 2].get_text()
                worksheet.write(fila, 14, madre)
            except:
                None
            continue
        
        #Información de hijos          
        if "Hijos" in elementos[i].get_text():
            hijos = elementos[i + 1:len(elementos) - 1]
            for id_h,hijo in enumerate(hijos):
                nombre_hijo = hijo.get_text()[4:]
                worksheet.write(fila, 16 + id_h, nombre_hijo)

#Especifico la dirección del Chrome Driver
ubicacion_driver = "D:\Yabra\Escritorio\\chromedriver.exe"


#Defino los Xpath que van a guiar mi búsqueda
xpaths = ['//*[@id="txt_Name"]', '//*[@id="txt_FamC"]', '//*[@id="txt_FamS"]' ,'//*[@id="optGeneroM"]',
              '//*[@id="txt_Birt_Date"]', '//*[@id="txt_Birt_Plac"]',
              '//*[@id="txt_Death_Date"]', '//*[@id="txt_Death_Plac"]', '//*[@id="txt_Comments"]', 
              '//*[@id="txt_Name_C"]', '//*[@id="txt_Wedding_Plac"]', '//*[@id="txt_Wedding_Date"]' ]

#Defino la funcion de búsqueda de xpaths
def busqueda_xpath(xpaths, fila):
    for id_path,path in enumerate(xpaths):
        #Hago el caso de búsqueda para el genero
        if id_path == 3:
            info = driver.find_elements_by_xpath(path)
            try:
                info = info[0]
                valor = info.get_attribute("checked")

                if valor == None:
                    worksheet.write_string(fila, 1 + id_path, "Femenino")
                else:
                    worksheet.write_string(fila, 1 + id_path, "Masculino")    
            except:
                None
        else:    
            info = driver.find_elements_by_xpath(path)
            try:
                info = info[0]
                valor = info.get_attribute("value")
                worksheet.write_string(fila, 1 + id_path, valor)
            except:
                None
                
#Empiezo abriendo el driver 
driver = webdriver.Chrome(executable_path= ubicacion_driver)

#Hago un loop a través de todos las urls de todas las letras
for i,lista in enumerate(lista_url[12:13]):   
    
    #Asigno la letra correspondiente
    letra = string.ascii_uppercase[i + 12]
    
    fila = 1
    
    #Creo un Excel para guardar los datos que se van recolectando     
    workbook = xlsxwriter.Workbook('Genealogias_' + str(letra) + '.xlsx', {'constant_memory': True})
    worksheet = workbook.add_worksheet()
    worksheet.write_string(0, 0, "Link")
    worksheet.write_string(0, 1, "Nombre")
    worksheet.write_string(0, 2, "Fam_C")
    worksheet.write_string(0, 3, "Fam_S")
    worksheet.write_string(0, 4, "Genero")
    worksheet.write_string(0, 5, "Fecha Nacimiento")
    worksheet.write_string(0, 6, "Lugar Nacimiento")
    worksheet.write_string(0, 7, "Fecha Defunción")
    worksheet.write_string(0, 8, "Lugar Defunción")
    worksheet.write_string(0, 9, "Comentarios")
    worksheet.write_string(0, 10, "Cónyugue")
    worksheet.write_string(0, 11, "Lugar Matrimonio")
    worksheet.write_string(0, 12, "Fecha Matrimonio")
    worksheet.write_string(0, 13, "Padre")
    worksheet.write_string(0, 14, "Madre")
    worksheet.write_string(0, 15, "Tipo Error")
  
    #Itero a través de las personas en la lista
    for persona in lista:
        
        #Pongo el link en el excel
        worksheet.write_string(fila, 0, persona)
        
        #Antes de ir a la páginas de la persona me aseguro de estar loggeado
        try:
            driver.set_page_load_timeout(45)
            driver.get("http://www.genealogiasdecolombia.co/Login.aspx") 
            usuario = driver.find_element_by_id("usr")
            usuario.send_keys(usuario_str)
                    
            clave = driver.find_element_by_id("pass")
            clave.send_keys(clave_str)
                    
            boton_siguiente = driver.find_element_by_id("btn_go1")
            boton_siguiente.click()
        
        except TimeoutException as ex:
            isrunning = 0
            print("Exception has been thrown. " + str(ex))
            driver.close()
            driver = webdriver.Chrome(executable_path= ubicacion_driver)
            worksheet.write_string(fila, 15, "Timeout")
            continue

        
        #Voy a la página de la persona
        try:
            driver.set_page_load_timeout(45)
            driver.get(persona)
            pagina_persona = requests.get(persona)
            contenido_pagina_persona = pagina_persona.content
            parser_pagina_persona = BeautifulSoup(contenido_pagina_persona, 'html.parser')
        
        except TimeoutException as ex:
            isrunning = 0
            print("Exception has been thrown. " + str(ex))
            driver.close()
            driver = webdriver.Chrome(executable_path= ubicacion_driver)
            worksheet.write_string(fila, 15, "Timeout")
            continue
        
        # Extraigo las tablas que hay en la página
        tablas = parser_pagina_persona.find_all("table")
                            
        if len(tablas) > 1:
            tabla = tablas[1]
            num_tablas = 2
        elif len(tablas) == 1:
            tabla = tablas[0]
            num_tablas = 1

        #Extraigo todos los elementos "td" de la tabla principal
        elementos = tabla.find_all("td")                
        
        #Si la tabla no tiene elementos, los extraigo todos
        if len(elementos) == 0:
            elementos = parser_pagina_persona.find_all("td")
            xpath_boton_editar = '//*[@id="Myproducts"]/table[' + str(num_tablas) + ']/tbody/tr[5]/td/h3/a'
        else: 
            xpath_boton_editar = '//*[@id="Myproducts"]/table[' + str(num_tablas) + ']/tbody/tr[3]/td/h3/a'
    
        #Edito el archivo de Excel con la información de padre, madre e hijos     
        editar_excel(tabla, elementos, fila)
        
        #Oprimo el botón para entrar a la página de edición
        boton_editar = driver.find_elements_by_xpath(xpath_boton_editar)
        
        try:
            boton_editar = boton_editar[0]
            boton_editar.click()
        except:
            worksheet.write_string(fila, 15, "NO HAY BOTÓN")
            fila = fila + 1
            continue
            
        busqueda_xpath(xpaths,fila)
        
        #Actualizo el contador de fila
        fila = fila + 1
    
    #Cierro el excel
    workbook.close()


