#importando funciones del modulo funciones_estrategia
from funciones_estrategia import todas_las_estrategias,inicializar_pares3,inicializar_pares2
import datetime
import time
#importando modulo para hacer search en strings
import re

#recogiendo datos del BOT


martillo_run = input("Desea aplicar las estrategias soporte long (s)(n): ")

if martillo_run == "s":
    normal_reverso_martillo = input("Desea aplicar las estrategias soporte long em modo (n)ormal o (r)everso: ")
    porx_martillo = input("indique el apalancamiento: ")
    monto_martillo = input("Indique el monto invertido por posicion: ")
    tp_martillo = input("Indique el Take profit em %: ")
    sl_martillo = input("Indique el Stop Loss em %: ")
    datos_martillo = [martillo_run,normal_reverso_martillo,porx_martillo, monto_martillo,tp_martillo,sl_martillo]
else:
    normal_reverso_martillo = ''
    porx_martillo = ''
    monto_martillo  = ''
    tp_martillo = ''
    sl_martillo  = ''
    datos_martillo = [martillo_run,normal_reverso_martillo,porx_martillo, monto_martillo,tp_martillo,sl_martillo] 

estrella_run = input("Desea aplicar las estrategias resistencia short (s)(n): ")

if estrella_run == "s":
    normal_reverso_estrella = input("Desea aplicar las estrategias resistencia short em modo (n)ormai o (r)everso: ")
    porx_estrella = input("indique el apalancamiento: ")
    monto_estrella = input("Indique el monto invertido por posicion: ")
    tp_estrella = input("Indique el Take profit em %: ")
    sl_estrella = input("Indique el Stop Loss em %: ")
    datos_estrella = [estrella_run,normal_reverso_estrella,porx_estrella, monto_estrella,tp_estrella,sl_estrella]
else:
    normal_reverso_estrella = ''
    porx_estrella = ''
    monto_estrella = ''
    tp_estrella = ''
    sl_estrella = ''
    datos_estrella = ''
    datos_estrella = [estrella_run,normal_reverso_estrella,porx_estrella, monto_estrella,tp_estrella,sl_estrella]

nro_velas = input("Indique el numero de velas a muestrear: ")

siclo = True
#inicializar_pares3()
inicializar_pares2()
while siclo:
    now = now = datetime.datetime.now()
    now_str = str(now)
    print(now_str)
    minute = 48
    while minute < 60:
        hora_buscada = re.search(f"06:{minute}:",now_str)
        hora_buscada_str = str(hora_buscada) 
        if hora_buscada_str != "None":
            print("esperando las 07:04")
            time.sleep(960 - 60*(minute -48))
        minute = minute + 1

    #estrategia_estrella(datos_estrella)
    #estrategia_martillo(datos_martillo)
    todas_las_estrategias(datos_martillo, datos_estrella, nro_velas)
    print("................................")
    print("................................")
    print("................................")
    print("................................")
    print("................................")
