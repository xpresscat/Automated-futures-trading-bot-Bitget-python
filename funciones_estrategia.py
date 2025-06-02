import pandas as pd
from funciones_bitget import leer_vela, crear_orden, verificar_si_posicion_abierta, obtener_precio_par, obtener_unprofit_posicion, cancel_position, lista_de_posiciones_abiertas
import datetime
#import vlc
import time

def recheckear_posiciones_abiertas(): 
    list_pos_open = list()                        
    lista_pares = pd.read_csv("pares2.csv")
    i = 0
    list_pos_open = lista_de_posiciones_abiertas()
    print(list_pos_open)
    while(lista_pares['par'][i] != "END"):
        par = lista_pares['par'][i]
        tp = lista_pares['tp'][i]
        sl = lista_pares['tp'][i] 
        for openpar in  list_pos_open:
            if par == openpar and tp == 0 and sl == 0:
                lista_pares.loc[i,'tp'] = -1
                lista_pares.loc[i,'sl'] = -1
                lista_pares.to_csv("pares2.csv",index=False)
        i = i + 1

#funcion para minimizar perdidas        
def tp_sl_automatico():
    unprofit_str = ""
    minimo = 8.0
    variacion_menos = 0.9
    variacion_mas = 1.0
    lista_pares = pd.read_csv("pares2.csv")
    lista_pares3 = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        par = lista_pares['par'][i]
        tp = lista_pares['tp'][i]
        sl = lista_pares['sl'][i]
        if tp != 0.0 and sl != 0.0:
            if verificar_si_posicion_abierta(par):
                unprofit_str = obtener_unprofit_posicion(par)
                if unprofit_str == "error":
                    return False
                unprofit = float(unprofit_str)   

                if tp != 0.0 and tp != -1.0:         
                    if unprofit <= tp  or unprofit <= -8:
                        cancel_position(par)
                        lista_pares.loc[i,'tp'] = 0.0
                        lista_pares.loc[i,'sl'] = 0.0  
                        lista_pares.to_csv("pares2.csv",index=False)
                        if unprofit <= -5:
                            lista_pares3.loc[i,'tp'] = 13
                        else:    
                            lista_pares3.loc[i,'tp'] = 13
                        lista_pares3.loc[i,'sl'] = 0
                        lista_pares3.to_csv("pares3.csv",index=False)
                    else:                                                  
                        if unprofit >= minimo and unprofit != 0.0:
                            if unprofit < (minimo + variacion_mas) and sl < minimo:
                                tp = minimo - variacion_menos
                                sl = minimo
                                lista_pares.loc[i,'tp'] = tp
                                lista_pares.loc[i,'sl'] = sl
                                lista_pares.to_csv("pares2.csv",index=False)
                            else:
                                if unprofit != 0.0 and unprofit > (sl + variacion_mas):
                                    indice = minimo + variacion_mas
                                    while (unprofit >= indice):
                                        tp = indice - variacion_menos
                                        sl = indice
                                        indice = indice + variacion_mas
                                    lista_pares.loc[i,'tp'] = tp
                                    lista_pares.loc[i,'sl'] = sl
                                    lista_pares.to_csv("pares2.csv",index=False)
                else:
                    if unprofit <= -8:
                        cancel_position(par)
                        lista_pares.loc[i,'tp'] = 0.0
                        lista_pares.loc[i,'sl'] = 0.0  
                        lista_pares.to_csv("pares2.csv",index=False)
                        lista_pares3.loc[i,'tp'] = 13
                        lista_pares3.loc[i,'sl'] = 0
                        lista_pares3.to_csv("pares3.csv",index=False)                       
                    if unprofit >= minimo and unprofit != 0.0:
                        if unprofit < (minimo + variacion_mas) and sl < minimo:
                            tp = minimo - variacion_menos
                            sl = minimo
                            lista_pares.loc[i,'tp'] = tp
                            lista_pares.loc[i,'sl'] = sl
                            lista_pares.to_csv("pares2.csv",index=False)
                        else:
                            if unprofit != 0.0 and unprofit > (sl + variacion_mas):
                                indice = minimo + variacion_mas
                                while (unprofit >= indice):
                                    tp = indice - variacion_menos
                                    sl = indice
                                    indice = indice + variacion_mas
                                lista_pares.loc[i,'tp'] = tp
                                lista_pares.loc[i,'sl'] = sl
                                lista_pares.to_csv("pares2.csv",index=False)
            else:
                if tp == -1.0 and sl == -1.0 and not(verificar_si_posicion_abierta(par)):
                    lista_pares.loc[i,'tp'] = 0.0
                    lista_pares.loc[i,'sl'] = 0.0  
                    lista_pares.to_csv("pares2.csv",index=False)   
        i = i + 1        

#colocar par em posicion en fichero csv
def colocar_par_en_posicion(par):
    lista_pares = pd.read_csv("pares2.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if lista_pares['par'][i] == par:
            lista_pares.loc[i,'tp'] = -1.0
            lista_pares.loc[i,'sl'] = -1.0           
        i = i + 1
    lista_pares.to_csv("pares2.csv",index=False)

#verificar las 3 ultimas velas antes de la ultima martillo
def verificar_3velas(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    emasn = 40
    emaln = 90
    Percent_Trading = 120
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 

    if nro < 3:
        print(nro)
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.032 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.030 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.032 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.030 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.032 * float(velas[nro-4][2]))
        variacion3A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.030 * float(velas[nro-4][3]))
        variacion3B = cuerpo2B / float(velas[nro-3][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100

    if nro > 3:

        if velas[nro-2][8] == "martillo" and float(velas[nro-1][4]) <= float(velas[nro-2][3]):
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")
            
            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-3][8] == "martillo" and float(velas[nro-1][4]) <= float(velas[nro-3][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-4][8] == "martillo" and float(velas[nro-1][4]) <= float(velas[nro-4][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-5][8] == "martillo" and float(velas[nro-1][4]) <= float(velas[nro-5][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-6][8] == "martillo" and float(velas[nro-1][4]) <= float(velas[nro-6][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-7][8] == "martillo" and float(velas[nro-1][4]) <= float(velas[nro-7][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-2][8] == "martillo" and float(velas[nro-1][4]) >= abs(float(velas[nro-2][2]) + 0.002 * float(velas[nro-2][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-3][8] == "martillo" and float(velas[nro-1][4]) >= abs(float(velas[nro-3][2]) + 0.002 * float(velas[nro-3][2])) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False
        
        #print("-------------")
        #print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        #print("-------------")
            
        #if Trading_Volumen_BC > Percent_Trading:
            #NorRev = "r"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            #date = datetime.datetime.now()
            #with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                #arch.writelines("Trading_Volumen_BC")  
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "bajada":
                #    NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "buy"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True              
    return False 


def verificar_3velas_resistencia(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    Percent_Trading = 120
    emasn = 40
    emaln = 90
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 

    if nro < 3:
        print(nro)
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.032 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.030 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.032 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.030 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.032 * float(velas[nro-4][2]))
        variacion3A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.030 * float(velas[nro-4][3]))
        variacion3B = cuerpo2B / float(velas[nro-3][1])

        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
       
    if nro > 3:

        if velas[nro-2][8] == "martillo" and float(velas[nro-1][4]) <= float(velas[nro-2][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")
            
            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-3][8] == "martillo" and float(velas[nro-1][4]) <= float(velas[nro-3][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-2][8] == "martillo" and float(velas[nro-1][4]) >= abs(float(velas[nro-2][2]) + 0.002 * float(velas[nro-2][2])):
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-3][8] == "martillo" and float(velas[nro-1][4]) >= abs(float(velas[nro-3][2]) + 0.002 * float(velas[nro-3][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-4][8] == "martillo" and float(velas[nro-1][4]) >= abs(float(velas[nro-4][2]) + 0.002 * float(velas[nro-4][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-5][8] == "martillo" and float(velas[nro-1][4]) >= abs(float(velas[nro-5][2]) + 0.002 * float(velas[nro-5][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-6][8] == "martillo" and float(velas[nro-1][4]) >= abs(float(velas[nro-6][2]) + 0.002 * float(velas[nro-6][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-7][8] == "martillo" and float(velas[nro-1][4]) >= abs(float(velas[nro-7][2]) + 0.002 * float(velas[nro-7][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False
        
        #print("-------------")
        #print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        #print("-------------")
            
        #if Trading_Volumen_BC > Percent_Trading:
            #NorRev = "n"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            #date = datetime.datetime.now()
            #with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                #arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "bajada":
                #    NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "buy"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True              
    return False 


#clasificar velas martillo
def clasificar_velas_martillo(velas):
    for vela in velas:
        #desempaquetando lista
        timestamp, Entry_price, Highest_price ,Lowest_price, Exit_price, trading_coin, Trading_currency, color, tipo = vela
        i = 0
        if color =='verde':
            mecha = float(Entry_price) - float(Lowest_price)
            cuerpo = float(Exit_price) - float(Entry_price)
            sombra = float(Highest_price)- float(Exit_price)
            if mecha >= 3 * cuerpo and sombra <= 1.5 * cuerpo and (cuerpo/float(Entry_price))>=0.0015:
                vela[8] = "martillo"
                
"""                    
#función estrategia martillo
def estrategia_martillo(param_list):
    #leyendo acrhivo csv con los pares de futuros de Bitge
    lista_pares = pd.read_csv("pares.csv")
    
    #desempaquetando lista
    extrat_run, NorRev, porx, monto, tp, sl, nro_velas  = param_list
    
    if extrat_run == "s":
        #aplicar extrategia a 15 min
        i = 0
        while(lista_pares['par'][i] != "END"):
            #leer velas
            print("Martillo")
            print(lista_pares['par'][i])
            print("Martillo")
            print(i)
            
            tp_sl_automatico()
            datos_vela = [lista_pares['par'][i],"1",nro_velas]
            velas = leer_vela(datos_vela)
            clasificar_velas_martllo(velas)
            verificar_3velas(velas,NorRev,porx,monto,tp,sl,lista_pares['par'][i])
            
            datos_vela = [lista_pares['par'][i],"0",nro_velas]
            velas = leer_vela(datos_vela)
            clasificar_velas_martllo(velas)
            verificar_3velas(velas,NorRev,porx,monto,tp,sl,lista_pares['par'][i])
            
            tp_sl_automatico()
            datos_vela = [lista_pares['par'][i],"2",nro_velas]
            velas = leer_vela(datos_vela)
            clasificar_velas_martllo(velas)
            verificar_3velas(velas,NorRev,porx,monto,tp,sl,lista_pares['par'][i])
            
            datos_vela = [lista_pares['par'][i],"3",nro_velas]
            velas = leer_vela(datos_vela)
            clasificar_velas_martllo(velas)
            verificar_3velas(velas,NorRev,porx,monto,tp,sl,lista_pares['par'][i])
            
            i = i + 1
""" 
 
 
#verificar las 3 ultimas velas antes de la ultima estrella
def verificar_3velas_estrella(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 79
    sobrevendido = 30
    Percent_Trading = 120
    emasn = 40
    emaln = 90
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 
    
    if nro < 3: 
        print(nro)   
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.030 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.032 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.030 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.032 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.030 * float(velas[nro-4][2]))
        variacion3A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.032 * float(velas[nro-4][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
        
    if nro > 3:
        
        if velas[nro-2][8] == "estrella" and float(velas[nro-1][4]) >= float(velas[nro-2][2]):
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-3][8] == "estrella" and float(velas[nro-1][4]) >= float(velas[nro-3][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-4][8] == "estrella" and float(velas[nro-1][4]) >= float(velas[nro-4][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-5][8] == "estrella" and float(velas[nro-1][4]) >= float(velas[nro-5][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-6][8] == "estrella" and float(velas[nro-1][4]) >= float(velas[nro-6][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-7][8] == "estrella" and float(velas[nro-1][4]) >= float(velas[nro-7][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-2][8] == "estrella" and float(velas[nro-1][4]) <= abs(float(velas[nro-2][3]) - 0.002 * float(velas[nro-2][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-3][8] == "estrella" and float(velas[nro-1][4]) <= abs(float(velas[nro-3][3]) - 0.002 * float(velas[nro-3][3])) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False
        
        #print("-------------")
        #print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        #print("-------------")
            
        #if Trading_Volumen_BC > Percent_Trading:
            #NorRev = "r"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            #date = datetime.datetime.now()
            #with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                #arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "subida":
                #    NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "buy"  
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True
    return False 


def verificar_3velas_estrella_soporte(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    Percent_Trading = 120
    emasn = 40
    emaln = 90
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 
    
    if nro < 3: 
        print(nro)   
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.030 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.032 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.030 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.032 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.030 * float(velas[nro-4][2]))
        variacion3A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.032 * float(velas[nro-4][3]))
        variacion3B = cuerpo2B / float(velas[nro-3][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
        
    if nro > 3:
        
        if velas[nro-2][8] == "estrella" and float(velas[nro-1][4]) >= float(velas[nro-2][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-3][8] == "estrella" and float(velas[nro-1][4]) >= float(velas[nro-3][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")
            
            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-2][8] == "estrella" and float(velas[nro-1][4]) <= abs(float(velas[nro-2][3]) - 0.002 * float(velas[nro-2][3])):
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-3][8] == "estrella" and float(velas[nro-1][4]) <= abs(float(velas[nro-3][3]) - 0.002 * float(velas[nro-3][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False
        
        if velas[nro-4][8] == "estrella" and float(velas[nro-1][4]) <= abs(float(velas[nro-4][3]) - 0.002 * float(velas[nro-4][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-5][8] == "estrella" and float(velas[nro-1][4]) <= abs(float(velas[nro-5][3]) - 0.002 * float(velas[nro-5][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-6][8] == "estrella" and float(velas[nro-1][4]) <= abs(float(velas[nro-6][3]) - 0.002 * float(velas[nro-6][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-7][8] == "estrella" and float(velas[nro-1][4]) <= abs(float(velas[nro-7][3]) - 0.002 * float(velas[nro-7][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False       
        
        #print("-------------")
        #print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        #print("-------------")
            
        #if Trading_Volumen_BC > Percent_Trading:
            #NorRev = "n"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            #date = datetime.datetime.now()
            #with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                #arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "subida":
                #    NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "buy"  
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True
    return False 
          
    
def clasificar_velas_estrella(velas):
    for vela in velas:
        #desempaquetando lista
        timestamp, Entry_price, Highest_price ,Lowest_price, Exit_price, trading_coin, Trading_currency, color, tipo = vela
        i = 0
        if color =='roja':
            mecha = float(Highest_price) - float(Entry_price)
            cuerpo = float(Entry_price) - float(Exit_price)
            sombra = float(Exit_price)- float(Lowest_price)
            if mecha >= 3 * cuerpo and sombra <= 1.5 * cuerpo and (cuerpo/float(Entry_price))>=0.0015:
                vela[8] = "estrella"  
                
"""
#función estrategia estrella
def estrategia_estrella(param_list):
    #leyendo acrhivo csv con los pares de futuros de Bitge
    lista_pares = pd.read_csv("pares.csv")
    
    #desempaquetando lista
    extrat_run, NorRev, porx, monto, tp, sl, nro_velas  = param_list
    
    if extrat_run == "s":
        #aplicar extrategia a 15 min
        i = 0
        while(lista_pares['par'][i] != "END"):
            #leer velas
            print("Estrella")
            print(lista_pares['par'][i])
            print("Estrella")
            print(i)
            
            tp_sl_automatico()
            datos_vela = [lista_pares['par'][i],"1",nro_velas]
            velas = leer_vela(datos_vela)
            clasificar_velas_estrella(velas)
            verificar_3velas_estrella(velas,NorRev,porx,monto,tp,sl,lista_pares['par'][i])
            
            datos_vela = [lista_pares['par'][i],"0",nro_velas]
            velas = leer_vela(datos_vela)
            clasificar_velas_estrella(velas)
            verificar_3velas_estrella(velas,NorRev,porx,monto,tp,sl,lista_pares['par'][i])
            
            tp_sl_automatico()
            datos_vela = [lista_pares['par'][i],"2",nro_velas]
            velas = leer_vela(datos_vela)
            clasificar_velas_estrella(velas)
            verificar_3velas_estrella(velas,NorRev,porx,monto,tp,sl,lista_pares['par'][i])
            
            datos_vela = [lista_pares['par'][i],"3",nro_velas]
            velas = leer_vela(datos_vela)
            clasificar_velas_estrella(velas)
            verificar_3velas_estrella(velas,NorRev,porx,monto,tp,sl,lista_pares['par'][i])
            
            i = i + 1
"""    
    
def colocar_tp_sl_virtual_float_csv(archivo):
    lista_pares = pd.read_csv(f"{archivo}.csv")
    
    lista_pares['tp'] =  lista_pares['tp'].astype(float)
    lista_pares['sl'] =  lista_pares['sl'].astype(float)
    
    lista_pares.to_csv(f"{archivo}.csv")
    
def leer_csv_type_tpsl(par):
    
    lista_pares = pd.read_csv("pares2.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        
        if lista_pares['par'][i] == par:
            return type(lista_pares['sl'][i])
        i = i + 1

def todas_las_estrategias(datos_martillo, datos_estrella, nro_velas):
    #leyendo acrhivo csv con los pares de futuros de Bitge
    lista_pares = pd.read_csv("pares.csv")
    
    #desempaquetando lista martillo
   
    extrat_run_martillo, NorRev_martillo, porx_martillo, monto_martillo, tp_martillo, sl_martillo = datos_martillo

    
    #desempaquetando lista estrella
    extrat_run_estrella, NorRev_estrella, porx_estrella, monto_estrella, tp_estrella, sl_estrella = datos_estrella

    i = 0
    while(lista_pares['par'][i] != "END"):
        print("------")
        print(lista_pares['par'][i])
        print(i)
        print("------")
        
        """
        #aplicar extrategia a 5 min 
        tp_sl_automatico()
        recheckear_posiciones_abiertas() 
        datos_vela = [lista_pares['par'][i],"0",nro_velas]
        velas = leer_vela(datos_vela)
        #correr estrategia martillo
        if extrat_run_martillo == "s":
            clasificar_velas_martllo(velas)
            CE_verificar_3velas("0", velas, lista_pares['par'][i])
            clasificar_velas_martllo_rojo(velas)
            CE_verificar_3velas_martillo_rojo("0", velas, lista_pares['par'][i])
            clasificar_velas_doji_verde(velas)
            CE_verificar_3velas_doji_verde_soporte("0", velas, lista_pares['par'][i])
        #correr estrategia estrella
        if extrat_run_estrella == "s":
            clasificar_velas_estrella(velas)
            CE_verificar_3velas_estrella("0", velas, lista_pares['par'][i])
            clasificar_velas_estrella_verde(velas)
            CE_verificar_3velas_estrella_verde("0", velas, lista_pares['par'][i])
            clasificar_velas_doji_rojo(velas)
            CE_verificar_3velas_doji_rojo_resistencia("0", velas, lista_pares['par'][i])       

         """   

        #aplicar extrategia a 15 min 
        tp_sl_automatico()
        recheckear_posiciones_abiertas() 
        datos_vela = [lista_pares['par'][i],"4",nro_velas]
        velas = leer_vela(datos_vela)
        #correr estrategia martillo
        if extrat_run_martillo == "s":
            clasificar_velas_martillo(velas)
            CE_verificar_3velas("4", velas, lista_pares['par'][i])
            clasificar_velas_martillo_rojo(velas)
            CE_verificar_3velas_martillo_rojo("4", velas, lista_pares['par'][i])
            #clasificar_velas_doji_verde(velas)
            #CE_verificar_3velas_doji_verde_soporte("4", velas, lista_pares['par'][i])
            #clasificar_velas_doji_rojo(velas)
            #CE_verificar_3velas_doji_rojo_soporte("4", velas, lista_pares['par'][i])
            clasificar_velas_estrella(velas)
            CE_verificar_3velas_estrella_soporte("4", velas, lista_pares['par'][i])
            clasificar_velas_estrella_verde(velas)
            CE_verificar_3velas_estrella_verde_soporte("4", velas, lista_pares['par'][i])
        #correr estrategia estrella
        if extrat_run_estrella == "s":
            clasificar_velas_estrella(velas)
            CE_verificar_3velas_estrella("4", velas, lista_pares['par'][i])
            clasificar_velas_estrella_verde(velas)
            CE_verificar_3velas_estrella_verde("4", velas, lista_pares['par'][i])
            #clasificar_velas_doji_rojo(velas)
            #CE_verificar_3velas_doji_rojo_resistencia("4", velas, lista_pares['par'][i])
            #clasificar_velas_doji_verde(velas)
            #CE_verificar_3velas_doji_verde_resistencia("4", velas, lista_pares['par'][i])
            clasificar_velas_martillo(velas)
            CE_verificar_3velas_resistencia("4", velas, lista_pares['par'][i])
            clasificar_velas_martillo_rojo(velas)
            CE_verificar_3velas_martillo_rojo_resistencia("4", velas, lista_pares['par'][i])
        
        #aplicar extrategia a 30m
        tp_sl_automatico()
        recheckear_posiciones_abiertas() 
        datos_vela = [lista_pares['par'][i],"2",nro_velas]
        velas = leer_vela(datos_vela)
        #correr estrategia martillo
        if extrat_run_martillo == "s":
            clasificar_velas_martillo(velas)
            CE_verificar_3velas("2", velas, lista_pares['par'][i])
            clasificar_velas_martillo_rojo(velas)
            CE_verificar_3velas_martillo_rojo("2", velas, lista_pares['par'][i])
            #clasificar_velas_doji_verde(velas)
            #CE_verificar_3velas_doji_verde_soporte("2", velas, lista_pares['par'][i])
            #clasificar_velas_doji_rojo(velas)
            #CE_verificar_3velas_doji_rojo_soporte("2", velas, lista_pares['par'][i])
            clasificar_velas_estrella(velas)
            CE_verificar_3velas_estrella_soporte("2", velas, lista_pares['par'][i])
            clasificar_velas_estrella_verde(velas)
            CE_verificar_3velas_estrella_verde_soporte("2", velas, lista_pares['par'][i])
        #correr estrategia estrella
        if extrat_run_estrella == "s":
            clasificar_velas_estrella(velas)
            CE_verificar_3velas_estrella("2", velas, lista_pares['par'][i])
            clasificar_velas_estrella_verde(velas)
            CE_verificar_3velas_estrella_verde("2", velas, lista_pares['par'][i])
            #clasificar_velas_doji_rojo(velas)
            #CE_verificar_3velas_doji_rojo_resistencia("2", velas, lista_pares['par'][i])
            #clasificar_velas_doji_verde(velas)
            #CE_verificar_3velas_doji_verde_resistencia("2", velas, lista_pares['par'][i]) 
            clasificar_velas_martillo(velas)
            CE_verificar_3velas_resistencia("2", velas, lista_pares['par'][i])
            clasificar_velas_martillo_rojo(velas)
            CE_verificar_3velas_martillo_rojo_resistencia("2", velas, lista_pares['par'][i])   
        
        #aplicar extrategia a 1h
        tp_sl_automatico()
        recheckear_posiciones_abiertas()
        datos_vela = [lista_pares['par'][i],"3",nro_velas]
        velas = leer_vela(datos_vela)
        #correr estrategia martillo
        if extrat_run_martillo == "s":
            clasificar_velas_martillo(velas)
            CE_verificar_3velas("3", velas, lista_pares['par'][i])
            clasificar_velas_martillo_rojo(velas)
            CE_verificar_3velas_martillo_rojo("3", velas, lista_pares['par'][i])
            #clasificar_velas_doji_verde(velas)
            #CE_verificar_3velas_doji_verde_soporte("3", velas, lista_pares['par'][i])
            #clasificar_velas_doji_rojo(velas)
            #CE_verificar_3velas_doji_rojo_soporte("3", velas, lista_pares['par'][i])
            clasificar_velas_estrella(velas)
            CE_verificar_3velas_estrella_soporte("3", velas, lista_pares['par'][i])
            clasificar_velas_estrella_verde(velas)
            CE_verificar_3velas_estrella_verde_soporte("3", velas, lista_pares['par'][i])
        #correr estrategia estrella
        if extrat_run_estrella == "s":
            clasificar_velas_estrella(velas)
            CE_verificar_3velas_estrella("3", velas, lista_pares['par'][i])
            clasificar_velas_estrella_verde(velas)
            CE_verificar_3velas_estrella_verde("3", velas, lista_pares['par'][i])
            #clasificar_velas_doji_rojo(velas)
            #CE_verificar_3velas_doji_rojo_resistencia("3", velas, lista_pares['par'][i])
            #clasificar_velas_doji_verde(velas)
            #CE_verificar_3velas_doji_verde_resistencia("3", velas, lista_pares['par'][i])
            clasificar_velas_martillo(velas)
            CE_verificar_3velas_resistencia("3", velas, lista_pares['par'][i])
            clasificar_velas_martillo_rojo(velas)
            CE_verificar_3velas_martillo_rojo_resistencia("3", velas, lista_pares['par'][i])   

        verificar_todas_las_estrategias(datos_martillo, datos_estrella, nro_velas)
        i = i + 1

def buscar_2puntos_soporte(velas,indice):
    puntos_soporte = 0
    nro = len(velas)
    i = nro - indice -3
    j = 0  
    
    if velas[i][7] == "verde":
        p1 = 1
    else:
        p1 = 4

    if velas[nro-indice][7] == "verde":
        p2 = 1
    else:
        p2 = 4

    vela_actual = float(velas[i][p1])
    vela_comparacion = float(velas[nro-indice][p2])
    intervalo_superior = vela_comparacion + 0.0027 * vela_comparacion
    intervalo_inferior = vela_comparacion - 0.0027 * vela_comparacion

    while vela_actual > intervalo_inferior and i > 0:
        if vela_actual <= intervalo_superior:
            if vela_actual >= intervalo_inferior:
                lista_soporte = puntos_soporte_continuo(velas,i,indice)
                j = int(lista_soporte[0])
                estado = lista_soporte[1] 
                if estado == True:
                    puntos_soporte = puntos_soporte + 1
                if puntos_soporte == 1:
                    if buscar_punto_superior(velas,intervalo_superior,indice,i) == True:
                        if buscar_punto_superior_entre_2_puntos(velas,intervalo_superior,i) == True:
                            return True
        i = i - 1 - j
        j = 0
        if i > 0:
            if velas[i][7] == "verde":
                p1 = 1
            else:
                p1 = 4  
            vela_actual = float(velas[i][p1]) 
        #if vela_actual > intervalo_inferior and i == 1:
            #return True                   
    return False

def puntos_soporte_continuo(velas,i,indice):
    puntos_soporte = 0
    estado = False
    nro = len(velas)
    j = i - 1
    if j > 0:
        if velas[j][7] == "verde":
            p1 = 1
        else:
            p1 = 4
    else:
        return [puntos_soporte, estado] 

    if velas[nro-indice][7] == "verde":
        p2 = 1
    else:
        p2 = 4

    vela_actual = float(velas[j][p1])
    vela_comparacion = float(velas[nro-indice][p2])
    intervalo_superior = vela_comparacion + 0.0027 * vela_comparacion
    intervalo_inferior = vela_comparacion - 0.0027 * vela_comparacion

    while vela_actual <= intervalo_superior and vela_actual >= intervalo_inferior and j > 0:
        puntos_soporte = puntos_soporte + 1
        j = j - 1
        if j > 0:
            if velas[j][7] == "verde":
                p1 = 1
            else:
                p1 = 4
        vela_actual = float(velas[j][p1])
    if vela_actual > intervalo_superior:
        estado = True
    else:
        estado = False
    return [puntos_soporte, estado] 

def buscar_punto_superior(velas,intervalo_superior,indice,rango_soporte):
    nro = len(velas)
    i = nro - indice - 3 
    rango_soporte = rango_soporte
    if velas[i][7] == "roja":
        p1 = 1
        p2 = 4
    else:
        p1 = 4
        p2 = 1
    vela_actual = float(velas[i][p1])
    vela_actual_abajo = float(velas[i][p2])
    punto_ideal_arriba = intervalo_superior + 0.017 * intervalo_superior

    while vela_actual_abajo > intervalo_superior and i > rango_soporte:
        if vela_actual >=  punto_ideal_arriba:
            return True
        i = i - 1
        if velas[i][7] == "roja":
            p1 = 1
            p2 = 4
        else:
            p1 = 4
            p2 = 1
        vela_actual = float(velas[i][p1])
        vela_actual_abajo = float(velas[i][p2])
    return False

def buscar_punto_superior_entre_2_puntos(velas,intervalo_superior,indice):
    nro = len(velas)
    i = indice + 1
    if velas[i][7] == "roja":
        p1 = 1
        p2 = 4
    else:
        p1 = 4
        p2 = 1
    vela_actual = float(velas[i][p1])
    vela_actual_abajo = float(velas[i][p2])
    punto_ideal_arriba = intervalo_superior + 0.017 * intervalo_superior

    while vela_actual_abajo > intervalo_superior and i < nro -1:
        if vela_actual >=  punto_ideal_arriba:
            return True
        i = i + 1
        if velas[i][7] == "roja":
            p1 = 1
            p2 = 4
        else:
            p1 = 4
            p2 = 1
        vela_actual = float(velas[i][p1])
        vela_actual_abajo = float(velas[i][p2])
    return False

def buscar_2puntos_resistencia(velas,indice):
    puntos_resistencia = 0
    nro = len(velas)
    i = nro - indice - 3
    j = 0 
 
    if velas[i][7] == "roja":
        p1 = 1
    else:
        p1 = 4

    if velas[nro-indice][7] == "roja":
        p2 = 1
    else:
        p2 = 4

    vela_actual = float(velas[i][p1])
    vela_comparacion = float(velas[nro-indice][p2])
    intervalo_superior = vela_comparacion + 0.0027 * vela_comparacion
    intervalo_inferior = vela_comparacion - 0.0027 * vela_comparacion

    while vela_actual < intervalo_superior and i > 0:
        if vela_actual <= intervalo_superior:
            if vela_actual >= intervalo_inferior:
                lista_resistencia = puntos_resistencia_continuo(velas,i,indice)
                j = int(lista_resistencia[0])
                estado = lista_resistencia[1] 
                if estado == True:
                    puntos_resistencia = puntos_resistencia + 1
                if puntos_resistencia == 1:
                    if buscar_punto_inferior(velas,intervalo_inferior,indice,i) == True:
                        if buscar_punto_inferior_entre_2_puntos(velas,intervalo_inferior,i) == True:
                            return True
        i = i - 1 - j
        j = 0
        if i > 0:
            if velas[i][7] == "roja":
                p1 = 1
            else:
                p1 = 4  
            vela_actual = float(velas[i][p1])  
        #if vela_actual < intervalo_superior and i == 1:
            #return True
    return False

def puntos_resistencia_continuo(velas,i,indice):
    puntos_resistencia = 0
    estado = False
    nro = len(velas)
    j = i - 1
    if j > 0:
        if velas[j][7] == "roja":
            p1 = 1
        else:
            p1 = 4
    else:
        return [puntos_resistencia, estado] 


    if velas[nro-indice][7] == "roja":
        p2 = 1
    else:
        p2 = 4

    vela_actual = float(velas[j][p1])
    vela_comparacion = float(velas[nro-indice][p2])
    intervalo_superior = vela_comparacion + 0.0027 * vela_comparacion
    intervalo_inferior = vela_comparacion - 0.0027 * vela_comparacion

    while vela_actual <= intervalo_superior and vela_actual >= intervalo_inferior and j > 0:
        puntos_resistencia = puntos_resistencia + 1
        j = j - 1
        if j > 0:
            if velas[j][7] == "roja":
                p1 = 1
            else:
                p1 = 4
        vela_actual = float(velas[j][p1])
    if vela_actual < intervalo_inferior:
        estado = True
    else:
        estado = False
    return [puntos_resistencia, estado] 


def buscar_punto_inferior(velas,intervalo_inferior,indice,rango_resistencia):
    nro = len(velas)
    i = nro - indice -3 
    rango_resistencia = rango_resistencia
    if velas[i][7] == "verde":
        p1 = 1
        p2 = 4
    else:
        p1 = 4
        p2 = 1
    vela_actual = float(velas[i][p1])
    vela_actual_arriba = float(velas[i][p2])
    punto_ideal_abajo = intervalo_inferior - 0.017 * intervalo_inferior

    while vela_actual_arriba < intervalo_inferior and i > rango_resistencia:
        if vela_actual <=  punto_ideal_abajo:
            return True
        i = i - 1
        if velas[i][7] == "verde":
            p1 = 1
            p2 = 4
        else:
            p1 = 4
            p2 = 1
        vela_actual = float(velas[i][p1])
        vela_actual_arriba = float(velas[i][p2])
    return False  

def buscar_punto_inferior_entre_2_puntos(velas,intervalo_inferior,indice):
    nro = len(velas)
    i = indice + 1
    if velas[i][7] == "verde":
        p1 = 1
        p2 = 4
    else:
        p1 = 4
        p2 = 1
    vela_actual = float(velas[i][p1])
    vela_actual_arriba = float(velas[i][p2])
    punto_ideal_abajo = intervalo_inferior - 0.017 * intervalo_inferior

    while vela_actual_arriba < intervalo_inferior and i < nro -1:
        if vela_actual <=  punto_ideal_abajo:
            return True
        i = i + 1
        if velas[i][7] == "verde":
            p1 = 1
            p2 = 4
        else:
            p1 = 4
            p2 = 1
        vela_actual = float(velas[i][p1])
        vela_actual_arriba = float(velas[i][p2])
    return False
    
def clasificar_velas_martillo_rojo(velas):
    for vela in velas:
        #desempaquetando lista
        timestamp, Entry_price, Highest_price ,Lowest_price, Exit_price, trading_coin, Trading_currency, color, tipo = vela
        i = 0
        if color =='roja':
            mecha = float(Exit_price) - float(Lowest_price)
            cuerpo = float(Entry_price) - float(Exit_price)
            sombra = float(Highest_price)- float(Entry_price)
            if mecha >= 3 * cuerpo and sombra <= 1.5 * cuerpo and (cuerpo/float(Entry_price))>=0.0015:
                vela[8] = "martillo_rojo"
                

def verificar_3velas_martillo_rojo(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    Percent_Trading = 120
    emasn = 40
    emaln = 90
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 

    if nro < 3:
        print(nro)
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.032 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.030 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.032 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.030 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.032 * float(velas[nro-4][2]))
        variacion3A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.030 * float(velas[nro-4][3]))
        variacion3B = cuerpo2B / float(velas[nro-3][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
        
    if nro > 3:

        if velas[nro-2][8] == "martillo_rojo" and float(velas[nro-1][4]) <= float(velas[nro-2][3]):
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")
            
            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-3][8] == "martillo_rojo" and float(velas[nro-1][4]) <= float(velas[nro-3][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-4][8] == "martillo_rojo" and float(velas[nro-1][4]) <= float(velas[nro-4][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-5][8] == "martillo_rojo" and float(velas[nro-1][4]) <= float(velas[nro-5][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-6][8] == "martillo_rojo" and float(velas[nro-1][4]) <= float(velas[nro-6][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-7][8] == "martillo_rojo" and float(velas[nro-1][4]) <= float(velas[nro-7][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False
        
        if velas[nro-2][8] == "martillo_rojo" and float(velas[nro-1][4]) >= abs(float(velas[nro-2][2]) + 0.002 * float(velas[nro-2][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-3][8] == "martillo_rojo" and float(velas[nro-1][4]) >= abs(float(velas[nro-3][2]) + 0.002 * float(velas[nro-3][2])) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False
        
        #print("-------------")
        #print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        #print("-------------")
            
        #if Trading_Volumen_BC > Percent_Trading:
            #NorRev = "r"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            #date = datetime.datetime.now()
            #with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                #arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "bajada":
                    #NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "buy"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True              
    return False 


def verificar_3velas_martillo_rojo_resistencia(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    Percent_Trading = 120
    emasn = 40
    emaln = 90
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 

    if nro < 3:
        print(nro)
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.032 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.030 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.032 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.030 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.032 * float(velas[nro-4][2]))
        variacion3A = cuerpo3A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.030 * float(velas[nro-4][3]))
        variacion3B = cuerpo3B / float(velas[nro-2][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
        
    if nro > 3:

        if velas[nro-2][8] == "martillo_rojo" and float(velas[nro-1][4]) <= float(velas[nro-2][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])
            
            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")
            
            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False

        if velas[nro-3][8] == "martillo_rojo" and float(velas[nro-1][4]) <= float(velas[nro-3][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
            else:
                cumple = False
        
        if velas[nro-2][8] == "martillo_rojo" and float(velas[nro-1][4]) >= abs(float(velas[nro-2][2]) + 0.002 * float(velas[nro-2][2])):
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-3][8] == "martillo_rojo" and float(velas[nro-1][4]) >= abs(float(velas[nro-3][2]) + 0.002 * float(velas[nro-3][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-4][8] == "martillo_rojo" and float(velas[nro-1][4]) >= abs(float(velas[nro-4][2]) + 0.002 * float(velas[nro-4][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-5][8] == "martillo_rojo" and float(velas[nro-1][4]) >= abs(float(velas[nro-5][2]) + 0.002 * float(velas[nro-5][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])


            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-6][8] == "martillo_rojo" and float(velas[nro-1][4]) >= abs(float(velas[nro-6][2]) + 0.002 * float(velas[nro-6][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-7][8] == "martillo_rojo" and float(velas[nro-1][4]) >= abs(float(velas[nro-7][2]) + 0.002 * float(velas[nro-7][2])) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
                NorRev = "r"
            else:
                cumple = False
        
        #print("-------------")
        #print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        #print("-------------")
            
        #if Trading_Volumen_BC > Percent_Trading:
            #NorRev = "n"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            #date = datetime.datetime.now()
            #with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                #arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "bajada":
                    #NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "buy"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True              
    return False

    
def clasificar_velas_estrella_verde(velas):
    for vela in velas:
        #desempaquetando lista
        timestamp, Entry_price, Highest_price ,Lowest_price, Exit_price, trading_coin, Trading_currency, color, tipo = vela
        i = 0
        if color =='verde':
            mecha = float(Highest_price) - float(Exit_price)
            cuerpo = float(Exit_price) - float(Entry_price)
            sombra = float(Entry_price)- float(Lowest_price)
            if mecha >= 3 * cuerpo and sombra <= 1.5 * cuerpo and (cuerpo/float(Entry_price))>=0.0015:
                vela[8] = "estrella_verde"  
                

def verificar_3velas_estrella_verde(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    Percent_Trading = 120
    emasn = 40
    emaln = 90
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 
    
    if nro < 3: 
        print(nro)  
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.030 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.032 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.030 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.032 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.030 * float(velas[nro-4][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.032 * float(velas[nro-4][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
    
    if nro > 3:
        
        if velas[nro-2][8] == "estrella_verde" and float(velas[nro-1][4]) >= float(velas[nro-2][2]):
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-3][8] == "estrella_verde" and float(velas[nro-1][4]) >= float(velas[nro-3][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-4][8] == "estrella_verde" and float(velas[nro-1][4]) >= float(velas[nro-4][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-5][8] == "estrella_verde" and float(velas[nro-1][4]) >= float(velas[nro-5][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-6][8] == "estrella_verde" and float(velas[nro-1][4]) >= float(velas[nro-6][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-7][8] == "estrella_verde" and float(velas[nro-1][4]) >= float(velas[nro-7][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False
        
        if velas[nro-2][8] == "estrella_verde" and float(velas[nro-1][4]) <= abs(float(velas[nro-2][3]) - 0.002 * float(velas[nro-2][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-3][8] == "estrella_verde" and float(velas[nro-1][4]) <= abs(float(velas[nro-3][3]) - 0.002 * float(velas[nro-3][3])) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False
        
        #print("-------------")
        #print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        #print("-------------")
            
        #if Trading_Volumen_BC > Percent_Trading:
            #NorRev = "r"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            #date = datetime.datetime.now()
            #with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                #arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "subida":
                    #NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "buy"  
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True
    return False


def verificar_3velas_estrella_verde_soporte(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    Percent_Trading = 120
    emasn = 40
    emaln = 90
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 
    
    if nro < 3: 
        print(nro)  
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.030 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.032 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.030 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.032 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.030 * float(velas[nro-4][2]))
        variacion3A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.032 * float(velas[nro-4][3]))
        variacion3B = cuerpo2B / float(velas[nro-3][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
        
    if nro > 3:
        
        if velas[nro-2][8] == "estrella_verde" and float(velas[nro-1][4]) >= float(velas[nro-2][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False

        if velas[nro-3][8] == "estrella_verde" and float(velas[nro-1][4]) >= float(velas[nro-3][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} < emal: {emal} < price:{price} and rsi14: {rsi14} > {sobrevendido}")
            print("-------------")

            if (emas < emal < price and rsi14 > sobrevendido):
                cumple = True
            else:
                cumple = False
        
        if velas[nro-2][8] == "estrella_verde" and float(velas[nro-1][4]) <= abs(float(velas[nro-2][3]) - 0.002 * float(velas[nro-2][3])):
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-3][8] == "estrella_verde" and float(velas[nro-1][4]) <= abs(float(velas[nro-3][3]) - 0.002 * float(velas[nro-3][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-4][8] == "estrella_verde" and float(velas[nro-1][4]) <= abs(float(velas[nro-4][3]) - 0.002 * float(velas[nro-4][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-5][8] == "estrella_verde" and float(velas[nro-1][4]) <= abs(float(velas[nro-5][3]) - 0.002 * float(velas[nro-5][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-6][8] == "estrella_verde" and float(velas[nro-1][4]) <= abs(float(velas[nro-6][3]) - 0.002 * float(velas[nro-6][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-7][8] == "estrella_verde" and float(velas[nro-1][4]) <= abs(float(velas[nro-7][3]) - 0.002 * float(velas[nro-7][3])) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)
            emas = obtener_ema(velas,nro-1,emasn)
            emal = obtener_ema(velas,nro-1,emaln)
            price = float(velas[nro-1][4])

            print("-------------")
            print(f"emas: {emas} > emal: {emal} > price:{price} and rsi14: {rsi14} < {sobrecomprado}")
            print("-------------")

            if (emas > emal > price and rsi14 < sobrecomprado):
                cumple = True
                NorRev = "r"
            else:
                cumple = False
        
        #print("-------------")
        #print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        #print("-------------")
            
        #if Trading_Volumen_BC > Percent_Trading:
            #NorRev = "n"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            #date = datetime.datetime.now()
            #with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                #arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "subida":
                    #NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "buy"  
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True
    return False


def clasificar_velas_doji_verde(velas):
    for vela in velas:
        #desempaquetando lista
        timestamp, Entry_price, Highest_price ,Lowest_price, Exit_price, trading_coin, Trading_currency, color, tipo = vela
        i = 0
        if color =='verde':
            mecha = float(Entry_price) - float(Lowest_price)
            cuerpo = float(Exit_price) - float(Entry_price)
            sombra = float(Highest_price) - float(Exit_price)
            if mecha >= 5 * cuerpo and sombra >= 5 * cuerpo and (cuerpo/float(Entry_price))<=0.0015:
                vela[8] = "doji_verde"  
                

def verificar_3velas_doji_verde_soporte(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    Percent_Trading = 120
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 
    
    if nro < 3:
        print(nro)  
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.030 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.030 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.030 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.030 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.030 * float(velas[nro-4][2]))
        variacion3A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.030 * float(velas[nro-4][3]))
        variacion3B = cuerpo2B / float(velas[nro-3][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
        
    if nro > 3:

        if velas[nro-2][8] == "doji_verde" and float(velas[nro-1][4]) <= float(velas[nro-2][3]):
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-2 doji_verde {par} {rsi14} <= {sobrevendido - 21}")
            print("-------------")

            if rsi14 <= sobrevendido - 21:
                cumple = True
            else:
                cumple = False  

        if velas[nro-3][8] == "doji_verde" and float(velas[nro-1][4]) <= float(velas[nro-3][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-3 doji_verde {par} {rsi14} <= {sobrevendido - 21}")
            print("-------------")

            if rsi14 <= sobrevendido - 21:
                cumple = True
            else:
                cumple = False 

        if velas[nro-4][8] == "doji_verde" and float(velas[nro-1][4]) <= float(velas[nro-4][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-4 doji_verde {par} {rsi14} <= {sobrevendido}")
            print("-------------")

            if rsi14 <= sobrevendido:
                cumple = True
            else:
                cumple = False
        
        if velas[nro-5][8] == "doji_verde" and float(velas[nro-1][4]) <= float(velas[nro-5][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-5 doji_verde {par} {rsi14} <= {sobrevendido}")
            print("-------------")

            if rsi14 <= sobrevendido:
                cumple = True
            else:
                cumple = False 

        if velas[nro-6][8] == "doji_verde" and float(velas[nro-1][4]) <= float(velas[nro-6][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-6 doji_verde {par} {rsi14} <= {sobrevendido}")
            print("-------------")

            if rsi14 <= sobrevendido:
                cumple = True
            else:
                cumple = False 

        if velas[nro-7][8] == "doji_verde" and float(velas[nro-1][4]) <= float(velas[nro-7][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-7 doji_verde {par} {rsi14} <= {sobrevendido}")
            print("-------------")

            if rsi14 <= sobrevendido:
                cumple = True
            else:
                cumple = False 

        if velas[nro-2][8] == "doji_verde" and float(velas[nro-1][4]) >= float(velas[nro-2][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-2 doji_verde {par} {rsi14} >= {sobrecomprado + 21}")
            print("-------------")

            if rsi14 >= sobrecomprado + 21:
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-3][8] == "doji_verde" and float(velas[nro-1][4]) >= float(velas[nro-3][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-3 doji_verde {par} {rsi14} >= {sobrecomprado + 21}")
            print("-------------")

            if rsi14 >= sobrecomprado + 21:
                cumple = True
                NorRev = "r"
            else:
                cumple = False
        
        print("-------------")
        print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        print("-------------")
            
        if Trading_Volumen_BC > Percent_Trading:
            NorRev = "r"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            date = datetime.datetime.now()
            with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "bajada":
                    #NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "buy"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True  
                    
    return False

def verificar_3velas_doji_verde_resistencia(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    Percent_Trading = 120
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 
    
    if nro < 3:
        print(nro) 
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.030 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.030 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.030 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.030 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.030 * float(velas[nro-4][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.030 * float(velas[nro-4][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
        
    if nro > 3:
        
        if velas[nro-2][8] == "doji_verde" and float(velas[nro-1][4]) >= float(velas[nro-2][2]):
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-2 doji_verde resistencia {par} {rsi14} >= {sobrecomprado + 21}")
            print("-------------")

            if rsi14 >= sobrecomprado + 21:
                cumple = True
            else:
                cumple = False

        if velas[nro-3][8] == "doji_verde" and float(velas[nro-1][4]) >= float(velas[nro-3][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-3 doji_verde resistencia {par} {rsi14} >= {sobrecomprado + 21}")
            print("-------------")

            if rsi14 >= sobrecomprado + 21:
                cumple = True
            else:
                cumple = False
        
        if velas[nro-4][8] == "doji_verde" and float(velas[nro-1][4]) >= float(velas[nro-4][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-4 doji_verde resistencia {par} {rsi14} >= {sobrecomprado}")
            print("-------------")

            if rsi14 >= sobrecomprado:
                cumple = True
            else:
                cumple = False

        if velas[nro-5][8] == "doji_verde" and float(velas[nro-1][4]) >= float(velas[nro-5][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-5 doji_verde resistencia {par} {rsi14} >= {sobrecomprado}")
            print("-------------")

            if rsi14 >= sobrecomprado:
                cumple = True
            else:
                cumple = False

        if velas[nro-6][8] == "doji_verde" and float(velas[nro-1][4]) >= float(velas[nro-6][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-6 doji_verde resistencia {par} {rsi14} >= {sobrecomprado}")
            print("-------------")

            if rsi14 >= sobrecomprado:
                cumple = True
            else:
                cumple = False

        if velas[nro-7][8] == "doji_verde" and float(velas[nro-1][4]) >= float(velas[nro-7][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-7 doji_verde resistencia {par} {rsi14} >= {sobrecomprado}")
            print("-------------")

            if rsi14 >= sobrecomprado:
                cumple = True
            else:
                cumple = False

        if velas[nro-2][8] == "doji_verde" and float(velas[nro-1][4]) <= float(velas[nro-2][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-2 doji_verde resistencia {par} {rsi14} <= {sobrevendido - 21}")
            print("-------------")

            if rsi14 <= sobrevendido - 21:
                cumple = True
                NorRev = "r"
            else:
                cumple = False  

        if velas[nro-3][8] == "doji_verde" and float(velas[nro-1][4]) <= float(velas[nro-3][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-3 doji_verde resistencia {par} {rsi14} <= {sobrevendido - 21}")
            print("-------------")

            if rsi14 <= sobrevendido - 21:
                cumple = True
                NorRev = "r"
            else:
                cumple = False 

        print("-------------")
        print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        print("-------------")
            
        if Trading_Volumen_BC > Percent_Trading:
            NorRev = "n"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            date = datetime.datetime.now()
            with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "subida":
                #    NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "buy"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True              
    
    return False 


"""""
    while i <=  2 and nro > 3:
        cuerpo = abs(float(velas[nro-2-i][4]) - float(velas[nro-2-i][1]))
        variacion = cuerpo / float(velas[nro-2][1])
        if nro > 3 and velas[nro-3-i][8] == "doji_verde" and velas[nro-5-i][7] == "roja" and velas[nro-4-i][7] == "roja" and velas[nro-2-i][7] == "verde" and variacion <= 0.01:
            #buscar si cumple punto de soporte
            cuerpo_mecha_vela_doji_verde = abs(float(velas[nro-3-i][1]) - float(velas[nro-3-i][3]))
            cuerpo_mecha_vela_posterior = abs(float(velas[nro-2-i][1]) - float(velas[nro-2-i][3]))
            if float(velas[nro-3-i][3]) <= float(velas[nro-2-i][3]):
                if velas[nro-1][7] == "roja" and float(velas[nro-1][4]) <= (float(velas[nro-3-i][1]) - 0.4 * cuerpo_mecha_vela_doji_verde):
                    cumple = buscar_2puntos_soporte(velas,3+i)
                    if cumple:
                        rsi = obtener_rsi(velas,nro-1)
                        if rsi <= sobrevendido:
                            cumple = True
                            i = 3
                        else:
                            cumple = False
            else:
                if velas[nro-1][7] == "roja" and float(velas[nro-1][4]) <= (float(velas[nro-2-i][1]) - 0.4 * cuerpo_mecha_vela_posterior):
                    cumple = buscar_2puntos_soporte(velas,3+i)
                    if cumple:
                        rsi = obtener_rsi(velas,nro-1)
                        if rsi <= sobrevendido:
                            cumple = True
                            i = 3
                        else:
                            cumple = False 
        i = i + 1
"""""

def clasificar_velas_doji_rojo(velas):
    for vela in velas:
        #desempaquetando lista
        timestamp, Entry_price, Highest_price ,Lowest_price, Exit_price, trading_coin, Trading_currency, color, tipo = vela
        i = 0
        if color =='roja':
            mecha = float(Highest_price) - float(Entry_price)
            cuerpo = float(Entry_price) - float(Exit_price)
            sombra = float(Exit_price)- float(Lowest_price)
            if mecha >= 5 * cuerpo and sombra >= 5 * cuerpo and (cuerpo/float(Entry_price))<=0.0015:
                vela[8] = "doji_rojo" 


def verificar_3velas_doji_rojo_resistencia(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    Percent_Trading = 120
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 
    
    if nro < 3:
        print(nro) 
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.030 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.030 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.030 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.030 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.030 * float(velas[nro-4][2]))
        variacion3A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.030 * float(velas[nro-4][3]))
        variacion3B = cuerpo2B / float(velas[nro-2][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
        
    if nro > 3:
        
        if velas[nro-2][8] == "doji_rojo" and float(velas[nro-1][4]) >= float(velas[nro-2][2]):
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-2 doji_rojo {par} {rsi14} >= {sobrecomprado + 21}")
            print("-------------")

            if rsi14 >= sobrecomprado + 21:
                cumple = True
            else:
                cumple = False

        if velas[nro-3][8] == "doji_rojo" and float(velas[nro-1][4]) >= float(velas[nro-3][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-3 doji_rojo {par} {rsi14} >= {sobrecomprado + 21}")
            print("-------------")

            if rsi14 >= sobrecomprado + 21:
                cumple = True
            else:
                cumple = False

        if velas[nro-4][8] == "doji_rojo" and float(velas[nro-1][4]) >= float(velas[nro-4][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-4 doji_rojo {par} {rsi14} >= {sobrecomprado}")
            print("-------------")

            if rsi14 >= sobrecomprado:
                cumple = True
            else:
                cumple = False

        if velas[nro-5][8] == "doji_rojo" and float(velas[nro-1][4]) >= float(velas[nro-5][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-5 doji_rojo {par} {rsi14} >= {sobrecomprado}")
            print("-------------")

            if rsi14 >= sobrecomprado:
                cumple = True
            else:
                cumple = False

        if velas[nro-6][8] == "doji_rojo" and float(velas[nro-1][4]) >= float(velas[nro-6][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-6 doji_rojo {par} {rsi14} >= {sobrecomprado}")
            print("-------------")

            if rsi14 >= sobrecomprado:
                cumple = True
            else:
                cumple = False

        if velas[nro-7][8] == "doji_rojo" and float(velas[nro-1][4]) >= float(velas[nro-7][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-7 doji_rojo {par} {rsi14} >= {sobrecomprado}")
            print("-------------")

            if rsi14 >= sobrecomprado:
                cumple = True
            else:
                cumple = False               

        if velas[nro-2][8] == "doji_rojo" and float(velas[nro-1][4]) <= float(velas[nro-2][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-2 doji_rojo {par} {rsi14} <= {sobrevendido - 21}")
            print("-------------")

            if rsi14 <= sobrevendido - 21:
                cumple = True
                NorRev = "r"
            else:
                cumple = False  

        if velas[nro-3][8] == "doji_rojo" and float(velas[nro-1][4]) <= float(velas[nro-3][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-3 doji_rojo {par} {rsi14} <= {sobrevendido - 21}")
            print("-------------")

            if rsi14 <= sobrevendido - 21:
                cumple = True
                NorRev = "r"
            else:
                cumple = False 

        print("-------------")
        print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        print("-------------")
            
        if Trading_Volumen_BC > Percent_Trading:
            NorRev = "r"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            date = datetime.datetime.now()
            with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "subida":
                #    NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "buy"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True              
    
    return False 

def verificar_3velas_doji_rojo_soporte(velas,NorRev,porx,monto,tp,sl,par):
    
    sobrecomprado = 70
    sobrevendido = 30
    Percent_Trading = 120
    nro = len(velas)
    cumple = False

    print("------------")  
    print("Entro") 
    print("------------") 
    
    if nro < 3:
        print(nro)  
    else: 
        cuerpo1A = abs(float(velas[nro-2][2]) + 0.030 * float(velas[nro-2][2])) #0.005 por apalancamiento 4   4 x 0.005  = 0.02 2 %
        variacion1A = cuerpo1A / float(velas[nro-1][1])
        cuerpo1B = abs(float(velas[nro-2][3]) - 0.030 * float(velas[nro-2][3]))
        variacion1B = cuerpo1B / float(velas[nro-1][1])

        cuerpo2A = abs(float(velas[nro-3][2]) + 0.030 * float(velas[nro-3][2]))
        variacion2A = cuerpo2A / float(velas[nro-2][1])
        cuerpo2B = abs(float(velas[nro-3][3]) - 0.030 * float(velas[nro-3][3]))
        variacion2B = cuerpo2B / float(velas[nro-2][1])

        cuerpo3A = abs(float(velas[nro-4][2]) + 0.030 * float(velas[nro-4][2]))
        variacion3A = cuerpo2A / float(velas[nro-2][1])
        cuerpo3B = abs(float(velas[nro-4][3]) - 0.030 * float(velas[nro-4][3]))
        variacion3B = cuerpo2B / float(velas[nro-3][1])
        
        Trading_Volumen_BC = abs(float(velas[nro-1][5]) - float(velas[nro-2][5]))
        Trading_Volumen_BC = (Trading_Volumen_BC / float(velas[nro-2][5])) * 100
        
    if nro > 3:

        if velas[nro-2][8] == "doji_rojo" and float(velas[nro-1][4]) <= float(velas[nro-2][3]):
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-2 doji_rojo soporte {par} {rsi14} <= {sobrevendido - 21}")
            print("-------------")

            if rsi14 <= sobrevendido - 21:
                cumple = True
            else:
                cumple = False  

        if velas[nro-3][8] == "doji_rojo" and float(velas[nro-1][4]) <= float(velas[nro-3][3]) and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-3 doji_rojo soporte {par} {rsi14} <= {sobrevendido - 21}")
            print("-------------")

            if rsi14 <= sobrevendido - 21:
                cumple = True
            else:
                cumple = False 

        if velas[nro-4][8] == "doji_rojo" and float(velas[nro-1][4]) <= float(velas[nro-4][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-4 doji_rojo soporte {par} {rsi14} <= {sobrevendido}")
            print("-------------")

            if rsi14 <= sobrevendido:
                cumple = True
            else:
                cumple = False 

        if velas[nro-5][8] == "doji_rojo" and float(velas[nro-1][4]) <= float(velas[nro-5][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-5 doji_rojo soporte {par} {rsi14} <= {sobrevendido}")
            print("-------------")

            if rsi14 <= sobrevendido:
                cumple = True
            else:
                cumple = False 

        if velas[nro-6][8] == "doji_rojo" and float(velas[nro-1][4]) <= float(velas[nro-6][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-6 doji_rojo soporte {par} {rsi14} <= {sobrevendido}")
            print("-------------")

            if rsi14 <= sobrevendido:
                cumple = True
            else:
                cumple = False 

        if velas[nro-7][8] == "doji_rojo" and float(velas[nro-1][4]) <= float(velas[nro-7][3]) and velas[nro-2][7] == "verde" and velas[nro-1][7] == "verde":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-7 doji_rojo soporte {par} {rsi14} <= {sobrevendido}")
            print("-------------")

            if rsi14 <= sobrevendido:
                cumple = True
            else:
                cumple = False 

        if velas[nro-2][8] == "doji_rojo" and float(velas[nro-1][4]) >= float(velas[nro-2][2]) and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-2 doji_rojo soporte {par} {rsi14} >= {sobrecomprado + 21}")
            print("-------------")

            if rsi14 >= sobrecomprado + 21:
                cumple = True
                NorRev = "r"
            else:
                cumple = False

        if velas[nro-3][8] == "doji_rojo" and float(velas[nro-1][4]) >= float(velas[nro-3][2]) and velas[nro-2][7] == "roja" and velas[nro-1][7] == "roja":
            rsi14 = obtener_rsi(velas,nro-1,14)

            print("-------------")
            print(f"rsi_n-3 doji_rojo soporte {par} {rsi14} >= {sobrecomprado + 21}")
            print("-------------")

            if rsi14 >= sobrecomprado + 21:
                cumple = True
                NorRev = "r"
            else:
                cumple = False
        
        print("-------------")
        print(f"Trading Volumen BC {Trading_Volumen_BC} > {Percent_Trading}")
        print("-------------")
            
        if Trading_Volumen_BC > Percent_Trading:
            NorRev = "r"
        
        if cumple:
            print("Se cumple condicion 3 velas")
            
            date = datetime.datetime.now()
            with open(f"Trading_Volumen_BC_{Trading_Volumen_BC}_rsi14_{rsi14}_NorRev_{NorRev}_{par}_{date}.txt","w") as arch:
                arch.writelines("Trading_Volumen_BC")
            
            if not(verificar_si_posicion_abierta(par)):
                #agregando los parametros de la orden a una variable lista
                precio_str = obtener_precio_par(par)
                #nro_velas = 3
                #if tendencia_par(par,"4",nro_velas) == "bajada":
                    #NorRev = "r"
                if NorRev == "n":
                    orden_tipo = "buy"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio + (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio - (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                else:
                    orden_tipo = "sell"
                    long = len(precio_str) 
                    precio = float(precio_str)   
                    tp_float = precio - (precio * float(tp))/100
                    tp_str = str(tp_float)
                    tp_str = tp_str[:long]
                    sl_float = precio + (precio * float(sl))/100
                    sl_str = str(sl_float)
                    sl_str = sl_str[:long]
                
                print(f"Take profit: {tp_str}")
                print(f"Stop loss: {sl_str}")
                datos_orden = [par,porx,monto,orden_tipo,tp_str,sl_str]
                #creando orden en Bitget
                crear_orden(datos_orden)
                colocar_par_en_posicion(par)
                return True  
                    
    return False


"""
    while i <=  2 and nro > 3:
        cuerpo = abs(float(velas[nro-2-i][1]) - float(velas[nro-2-i][4]))
        variacion = cuerpo / float(velas[nro-2][1])
        if nro > 3 and velas[nro-3-i][8] == "doji_rojo" and velas[nro-5-i][7] == "verde" and velas[nro-4-i][7] == "verde" and velas[nro-2-i][7] == "roja" and variacion <= 0.01:
            #buscar si cumple punto de soporte
            cuerpo_sombra_vela_doji_rojo = abs(float(velas[nro-3-i][2]) - float(velas[nro-3-i][1]))
            cuerpo_sombra_vela_posterior = abs(float(velas[nro-2-i][2]) - float(velas[nro-2-i][1]))
            if float(velas[nro-3-i][2]) >= float(velas[nro-2-i][2]):
                if velas[nro-1][7] == "verde" and float(velas[nro-1][4]) >= (float(velas[nro-3-i][1]) + 0.4 * cuerpo_sombra_vela_doji_rojo):
                    cumple = buscar_2puntos_soporte(velas,3+i)
                    if cumple:
                        rsi = obtener_rsi(velas,nro-1)
                        if rsi >= sobrecomprado:
                            cumple = True
                            i = 3
                        else:
                            cumple = False
            else:
                if velas[nro-1][7] == "verde" and float(velas[nro-1][4]) >= (float(velas[nro-2-i][1]) + 0.4 * cuerpo_sombra_vela_posterior):
                    cumple = buscar_2puntos_soporte(velas,3+i)
                    if cumple:
                        rsi = obtener_rsi(velas,nro-1)
                        if rsi >= sobrecomprado:
                            cumple = True
                            i = 3
                        else:
                            cumple = False
        i = i + 1
"""

def CE_verificar_3velas(intervalo, velas, par):
    nro = len(velas)
    estrategia = 1
    if nro < 3:
        print(nro) 
    else: 
        cuerpo3 = abs(float(velas[nro-3][1]) - float(velas[nro-3][4]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][1])-float(velas[nro-4][4]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])  

    if nro > 3 and velas[nro-2][8] == "martillo" and velas[nro-4][7] == "roja" and velas[nro-3][7] == "roja":
        #buscar si cumple punto de soporte

        cumple = buscar_2puntos_soporte(velas,2)
        
        if cumple:                   
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia) 
                        lista_pares.to_csv("pares3.csv",index=False) 
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"martillo_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("martillo")
                        
                i = i + 1     
    else:
        return False
    
def CE_verificar_3velas_martillo_rojo(intervalo, velas, par):
    nro = len(velas)
    estrategia = 2
    if nro < 3:
        print(nro)  
    else: 
        cuerpo3 = abs(float(velas[nro-3][1]) - float(velas[nro-3][4]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][1])-float(velas[nro-4][4]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])  
 

    if nro > 3 and velas[nro-2][8] == "martillo_rojo" and velas[nro-4][7] == "roja" and velas[nro-3][7] == "roja":
        #buscar si cumple punto de soporte
   
        cumple = buscar_2puntos_soporte(velas,2)
      
        if cumple:
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia) 
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"martillo_rojo_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("martillo_rojo")  

                i = i + 1      
    else:
        return False
    
def CE_verificar_3velas_doji_verde_soporte(intervalo, velas, par):
    nro = len(velas)
    estrategia = 3
    if nro < 3:
        print(nro) 
    else: 
        cuerpo3 = abs(float(velas[nro-3][1]) - float(velas[nro-3][4]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][1])-float(velas[nro-4][4]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])    

    if nro > 3 and velas[nro-2][8] == "doji_verde" and velas[nro-4][7] == "roja" and velas[nro-3][7] == "roja":
        #buscar si cumple punto de soporte

        cumple = buscar_2puntos_soporte(velas,2)
        
        if cumple:       
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia) 
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"doji_verde_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("dojo_verde")  

                i = i + 1     
    else:
        return False 


def CE_verificar_3velas_doji_rojo_soporte(intervalo, velas, par):
    nro = len(velas)
    estrategia = 4
    if nro < 3:
        print(nro)
    else: 
        cuerpo3 = abs(float(velas[nro-3][1]) - float(velas[nro-3][4]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][1])-float(velas[nro-4][4]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])   

    if nro > 3 and velas[nro-2][8] == "doji_rojo" and velas[nro-4][7] == "roja" and velas[nro-3][7] == "roja":
        #buscar si cumple punto de soporte 
         
        cumple = buscar_2puntos_soporte(velas,2)

        if cumple:            
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    print(par)
                    print(lista_pares.loc[i,'tp'])
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia)
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"doji_rojo_soporte_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("doji_rojo_soporte")  

                i = i + 1  
    else:
        return False
    

def CE_verificar_3velas_estrella_soporte(intervalo, velas, par):
    nro = len(velas)
    estrategia = 5
    if nro < 3:
        print(nro)
    else: 
        cuerpo3 = abs(float(velas[nro-3][1]) - float(velas[nro-3][4]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][1])-float(velas[nro-4][4]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])   

    if nro > 3 and velas[nro-2][8] == "estrella" and velas[nro-4][7] == "roja" and velas[nro-3][7] == "roja":
        #buscar si cumple punto de soporte 
         
        cumple = buscar_2puntos_soporte(velas,2)

        if cumple:            
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    print(par)
                    print(lista_pares.loc[i,'tp'])
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia)
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"estrella_soporte_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("estralla_soporte")  

                i = i + 1  
    else:
        return False
    

def CE_verificar_3velas_estrella_verde_soporte(intervalo, velas, par):
    nro = len(velas)
    estrategia = 6
    if nro < 3:
        print(nro)
    else: 
        cuerpo3 = abs(float(velas[nro-3][1]) - float(velas[nro-3][4]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][1])-float(velas[nro-4][4]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])   

    if nro > 3 and velas[nro-2][8] == "estrella_verde" and velas[nro-4][7] == "roja" and velas[nro-3][7] == "roja":
        #buscar si cumple punto de soporte 
         
        cumple = buscar_2puntos_soporte(velas,2)

        if cumple:            
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    print(par)
                    print(lista_pares.loc[i,'tp'])
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia)
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"estrella_verde_soporte_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("estralla_verde_soporte")  

                i = i + 1  
    else:
        return False
    

def CE_verificar_3velas_estrella(intervalo, velas, par):
    nro = len(velas)
    estrategia = 7
    if nro < 3:
        print(nro)
    else: 
        cuerpo3 = abs(float(velas[nro-3][4]) - float(velas[nro-3][1]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][4])-float(velas[nro-4][1]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])    

    if nro > 3 and velas[nro-2][8] == "estrella" and velas[nro-4][7] == "verde" and velas[nro-3][7] == "verde":
        #buscar si cumple punto de soporte
     
        cumple = buscar_2puntos_resistencia(velas,2)
        
        if cumple:
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia) 
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"estrella_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("estrella")  

                i = i + 1      
    else:
        return False
    

def CE_verificar_3velas_estrella_verde(intervalo, velas, par):
    nro = len(velas)
    estrategia = 8
    if nro < 3:
        print(nro)
    else: 
        cuerpo3 = abs(float(velas[nro-3][4]) - float(velas[nro-3][1]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][4])-float(velas[nro-4][1]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])   

    if nro > 3 and velas[nro-2][8] == "estrella_verde" and velas[nro-4][7] == "verde" and velas[nro-3][7] == "verde":
        #buscar si cumple punto de soporte
     
        cumple = buscar_2puntos_resistencia(velas,2)
        
        if cumple:              
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia) 
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"estrella_verde_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("estrella_verde")  
                i = i + 1     
    else:
        return False


def CE_verificar_3velas_doji_rojo_resistencia(intervalo, velas, par):
    nro = len(velas)
    estrategia = 9
    if nro < 3:
        print(nro)
    else: 
        cuerpo3 = abs(float(velas[nro-3][4]) - float(velas[nro-3][1]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][4])-float(velas[nro-4][1]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])   

    if nro > 3 and velas[nro-2][8] == "doji_rojo" and velas[nro-4][7] == "verde" and velas[nro-3][7] == "verde":
        #buscar si cumple punto de soporte 
         
        cumple = buscar_2puntos_resistencia(velas,2)

        if cumple:            
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    print(par)
                    print(lista_pares.loc[i,'tp'])
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia)
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"doji_rojo_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("doji_rojo")  

                i = i + 1  
    else:
        return False
    

def CE_verificar_3velas_doji_verde_resistencia(intervalo, velas, par):
    nro = len(velas)
    estrategia = 10
    if nro < 3:
        print(nro) 
    else: 
        cuerpo3 = abs(float(velas[nro-3][4]) - float(velas[nro-3][1]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][4])-float(velas[nro-4][1]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])   

    if nro > 3 and velas[nro-2][8] == "doji_verde" and velas[nro-4][7] == "verde" and velas[nro-3][7] == "verde":
        #buscar si cumple punto de soporte

        cumple = buscar_2puntos_resistencia(velas,2)
        
        if cumple:       
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia) 
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"doji_verde_resistencia_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("dojo_verde_resistencia")  

                i = i + 1     
    else:
        return False


def CE_verificar_3velas_resistencia(intervalo, velas, par):
    nro = len(velas)
    estrategia = 11
    if nro < 3:
        print(nro) 
    else: 
        cuerpo3 = abs(float(velas[nro-3][4]) - float(velas[nro-3][1]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][4])-float(velas[nro-4][1]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])   

    if nro > 3 and velas[nro-2][8] == "martillo" and velas[nro-4][7] == "verde" and velas[nro-3][7] == "verde":
        #buscar si cumple punto de soporte

        cumple = buscar_2puntos_resistencia(velas,2)
        
        if cumple:       
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia) 
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"martillo_resistencia_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("martillo_resistencia")  

                i = i + 1     
    else:
        return False
    

def CE_verificar_3velas_martillo_rojo_resistencia(intervalo, velas, par):
    nro = len(velas)
    estrategia = 12
    if nro < 3:
        print(nro) 
    else: 
        cuerpo3 = abs(float(velas[nro-3][4]) - float(velas[nro-3][1]))
        variacion3 = cuerpo3 / float(velas[nro-3][1])
        cuerpo4 = abs(float(velas[nro-4][4])-float(velas[nro-4][1]))
        variacion4 = cuerpo4 / float(velas[nro-4][1])   

    if nro > 3 and velas[nro-2][8] == "martillo_rojo" and velas[nro-4][7] == "verde" and velas[nro-3][7] == "verde":
        #buscar si cumple punto de soporte

        cumple = buscar_2puntos_resistencia(velas,2)
        
        if cumple:       
            print("Se cumple condicion 3 velas")
            lista_pares = pd.read_csv("pares3.csv")
            i = 0
            while(lista_pares['par'][i] != "END"):
                if par == lista_pares['par'][i]:
                    if lista_pares.loc[i,'tp'] == 13:
                        lista_pares.loc[i,'tp'] = int(intervalo)
                        lista_pares.loc[i,'sl'] = int(estrategia) 
                        lista_pares.to_csv("pares3.csv",index=False)
                        #verificacion
                        date = datetime.datetime.now()
                        with open(f"martillo_rojo_resistencia_{par}_{intervalo}_{estrategia}_{date}.txt","w") as arch:
                            arch.writelines("martillo_rojo_resistencia")  

                i = i + 1     
    else:
        return False
    
    
def verificar_todas_las_estrategias(datos_martillo, datos_estrella, nro_velas):
    #leyendo acrhivo csv con los pares de futuros de Bitge
    lista_pares = pd.read_csv("pares3.csv")
    
    #desempaquetando lista martillo
    extrat_run_martillo, NorRev_martillo, porx_martillo, monto_martillo, tp_martillo, sl_martillo = datos_martillo

    #desempaquetando lista estrella
    extrat_run_estrella, NorRev_estrella, porx_estrella, monto_estrella, tp_estrella, sl_estrella = datos_estrella

    i = 0
    while(lista_pares['par'][i] != "END"):
        par = lista_pares['par'][i]

        if lista_pares.loc[i,'sl'] == 1 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_martillo == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_martillo(velas)
                if verificar_3velas(velas,NorRev_martillo,porx_martillo,monto_martillo,tp_martillo,sl_martillo,par) == True:
                    CFR_verificar_3velas(par)
                VFR_verificar_3velas(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: martillo")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")

        if lista_pares.loc[i,'sl'] == 2 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_martillo == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_martillo_rojo(velas)
                if verificar_3velas_martillo_rojo(velas,NorRev_martillo,porx_martillo,monto_martillo,tp_martillo,sl_martillo,par) == True:
                    CFR_verificar_3velas_martillo_rojo(par)
                VFR_verificar_3velas_martillo_rojo(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: martillo rojo")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")
        
        if lista_pares.loc[i,'sl'] == 3 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_martillo == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_doji_verde(velas)
                if verificar_3velas_doji_verde_soporte(velas,NorRev_martillo,porx_martillo,monto_martillo,tp_martillo,sl_martillo,par) == True:
                    CFR_verificar_3velas_doji_verde_soporte(par)
                VFR_verificar_3velas_doji_verde_soporte(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: doji verde soporte")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")      

        if lista_pares.loc[i,'sl'] == 4 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_estrella == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_doji_rojo(velas)
                if verificar_3velas_doji_rojo_soporte(velas,NorRev_martillo,porx_martillo,monto_martillo,tp_martillo,sl_martillo,par) == True:
                    CFR_verificar_3velas_doji_rojo_soporte(par)
                VFR_verificar_3velas_doji_rojo_soporte(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: doji rojo soporte")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")
        
        if lista_pares.loc[i,'sl'] == 5 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_estrella == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_estrella(velas)
                if verificar_3velas_estrella_soporte(velas,NorRev_martillo,porx_martillo,monto_martillo,tp_martillo,sl_martillo,par) == True:
                    CFR_verificar_3velas_estrella_soporte(par)
                VFR_verificar_3velas_estrella_soporte(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: estrella soporte")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")

        if lista_pares.loc[i,'sl'] == 6 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_estrella == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_estrella_verde(velas)
                if verificar_3velas_estrella_verde_soporte(velas,NorRev_martillo,porx_martillo,monto_martillo,tp_martillo,sl_martillo,par) == True:
                    CFR_verificar_3velas_estrella_verde_soporte(par)
                VFR_verificar_3velas_estrella_verde_soporte(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: estrella verde soporte")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")

        if lista_pares.loc[i,'sl'] == 7 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_estrella == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_estrella(velas)
                if verificar_3velas_estrella(velas,NorRev_estrella,porx_estrella,monto_estrella,tp_estrella,sl_estrella,par) == True:
                    CFR_verificar_3velas_estrella(par)
                VFR_verificar_3velas_estrella(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: estrella")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")

        if lista_pares.loc[i,'sl'] == 8 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_estrella == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_estrella_verde(velas)
                if verificar_3velas_estrella_verde(velas,NorRev_estrella,porx_estrella,monto_estrella,tp_estrella,sl_estrella,par) == True:
                    CFR_verificar_3velas_estrella_verde(par)
                VFR_verificar_3velas_estrella_verde(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: estrella verde")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")

        if lista_pares.loc[i,'sl'] == 9 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_estrella == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_doji_rojo(velas)
                if verificar_3velas_doji_rojo_resistencia(velas,NorRev_estrella,porx_estrella,monto_estrella,tp_estrella,sl_estrella,par) == True:
                    CFR_verificar_3velas_doji_rojo_resistencia(par)
                VFR_verificar_3velas_doji_rojo_resistencia(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: doji rojo resistencia")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")

        if lista_pares.loc[i,'sl'] == 10 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_martillo == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_doji_verde(velas)
                if verificar_3velas_doji_verde_resistencia(velas,NorRev_estrella,porx_estrella,monto_estrella,tp_estrella,sl_estrella,par) == True:
                    CFR_verificar_3velas_doji_verde_resistencia(par)
                VFR_verificar_3velas_doji_verde_resistencia(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: doji verde resistencia")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")

        if lista_pares.loc[i,'sl'] == 11 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_martillo == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_martillo(velas)
                if verificar_3velas_resistencia(velas,NorRev_estrella,porx_estrella,monto_estrella,tp_estrella,sl_estrella,par) == True:
                    CFR_verificar_3velas_resistencia(par)
                VFR_verificar_3velas_resistencia(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: martillo resistencia")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")

        if lista_pares.loc[i,'sl'] == 12 and lista_pares.loc[i,'tp'] != 13:
            if extrat_run_martillo == "s":
                intervalo = str(lista_pares.loc[i,'tp'])
                datos_vela = [par,intervalo,nro_velas]
                velas = leer_vela(datos_vela)
                clasificar_velas_martillo_rojo(velas)
                if verificar_3velas_martillo_rojo_resistencia(velas,NorRev_estrella,porx_estrella,monto_estrella,tp_estrella,sl_estrella,par) == True:
                    CFR_verificar_3velas_martillo_rojo_resistencia(par)
                VFR_verificar_3velas_martillo_rojo_resistencia(velas,lista_pares,i)
                print("-.-.-.-.-")
                print(par)
                print("estrategia: martillo rojo resistencia")
                print(f"Intervalo: {intervalo}")
                print("-.-.-.-.-")

        i = i + 1
        

def VFR_verificar_3velas(velas,lista_pares,i):
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "martillo" or velas[nro-6][8] == "martillo" or velas[nro-5][8] == "martillo" or velas[nro-4][8] == "martillo" or velas[nro-3][8] == "martillo" or velas[nro-2][8] == "martillo":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False
        
def CFR_verificar_3velas(par):

    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False
    
def VFR_verificar_3velas_martillo_rojo(velas,lista_pares,i):       
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "martillo_rojo" or velas[nro-6][8] == "martillo_rojo" or velas[nro-5][8] == "martillo_rojo" or velas[nro-4][8] == "martillo_rojo" or velas[nro-3][8] == "martillo_rojo" or velas[nro-2][8] == "martillo_rojo":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False

def CFR_verificar_3velas_martillo_rojo(par):
   
    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False

def VFR_verificar_3velas_doji_verde_soporte(velas,lista_pares,i):    
    
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "doji_verde" or velas[nro-6][8] == "doji_verde" or velas[nro-5][8] == "doji_verde" or velas[nro-4][8] == "doji_verde" or velas[nro-3][8] == "doji_verde" or velas[nro-2][8] == "doji_verde":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False

    """
    nro = len(velas)
    j = 0
    if nro < 3:
        print(nro)

    if nro > 3:
        while j <= 2:
            if velas[nro-3-j][8] == "doji_verde" or velas[nro-2-j][8] == "doji_verde":
                return True
            j = j + 1
        lista_pares.loc[i,'tp'] = 8
        lista_pares.to_csv("pares3.csv",index=False)
        return False
    return False
    """ 
    
def CFR_verificar_3velas_doji_verde_soporte(par): 
     
    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False


def VFR_verificar_3velas_doji_rojo_soporte(velas,lista_pares,i):       
    
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "doji_rojo" or velas[nro-6][8] == "doji_rojo" or velas[nro-5][8] == "doji_rojo" or velas[nro-4][8] == "doji_rojo" or velas[nro-3][8] == "doji_rojo" or velas[nro-2][8] == "doji_rojo":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False


def CFR_verificar_3velas_doji_rojo_soporte(par):

    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False

def VFR_verificar_3velas_estrella_soporte(velas,lista_pares,i):       
    
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "estrella" or velas[nro-6][8] == "estrella" or velas[nro-5][8] == "estrella" or velas[nro-4][8] == "estrella" or velas[nro-3][8] == "estrella" or velas[nro-2][8] == "estrella":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False

def CFR_verificar_3velas_estrella_soporte(par):

    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False


def VFR_verificar_3velas_estrella_verde_soporte(velas,lista_pares,i):       
    
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "estrella_verde" or velas[nro-6][8] == "estrella_verde" or velas[nro-5][8] == "estrella_verde" or velas[nro-4][8] == "estrella_verde" or velas[nro-3][8] == "estrella_verde" or velas[nro-2][8] == "estrella_verde":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False


def CFR_verificar_3velas_estrella_verde_soporte(par):

    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False


def VFR_verificar_3velas_estrella(velas,lista_pares,i): 
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "estrella" or velas[nro-6][8] == "estrella" or velas[nro-5][8] == "estrella" or velas[nro-4][8] == "estrella" or velas[nro-3][8] == "estrella" or velas[nro-2][8] == "estrella":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False

def CFR_verificar_3velas_estrella(par): 

    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False

def VFR_verificar_3velas_estrella_verde(velas,lista_pares,i):
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "estrella_verde" or velas[nro-6][8] == "estrella_verde" or velas[nro-5][8] == "estrella_verde" or velas[nro-4][8] == "estrella_verde" or velas[nro-3][8] == "estrella_verde" or velas[nro-2][8] == "estrella_verde":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False

def CFR_verificar_3velas_estrella_verde(par):

    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False

def VFR_verificar_3velas_doji_rojo_resistencia(velas,lista_pares,i):       
    
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "doji_rojo" or velas[nro-6][8] == "doji_rojo" or velas[nro-5][8] == "doji_rojo" or velas[nro-4][8] == "doji_rojo" or velas[nro-3][8] == "doji_rojo" or velas[nro-2][8] == "doji_rojo":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False

    """
    nro = len(velas)
    j = 0
    if nro < 3:
        print(nro)   

    if nro > 3:
        while j <= 2:
            if velas[nro-3-j][8] == "doji_rojo" or velas[nro-2-j][8] == "doji_rojo":
                return True
            j = j + 1
        lista_pares.loc[i,'tp'] = 8
        lista_pares.to_csv("pares3.csv",index=False)
        return False
    return False
    """

def CFR_verificar_3velas_doji_rojo_resistencia(par):

    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False


def VFR_verificar_3velas_doji_verde_resistencia(velas,lista_pares,i):    
    
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "doji_verde" or velas[nro-6][8] == "doji_verde" or velas[nro-5][8] == "doji_verde" or velas[nro-4][8] == "doji_verde" or velas[nro-3][8] == "doji_verde" or velas[nro-2][8] == "doji_verde":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False


def CFR_verificar_3velas_doji_verde_resistencia(par):

    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False


def VFR_verificar_3velas_resistencia(velas,lista_pares,i):
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "martillo" or velas[nro-6][8] == "martillo" or velas[nro-5][8] == "martillo" or velas[nro-4][8] == "martillo" or velas[nro-3][8] == "martillo" or velas[nro-2][8] == "martillo":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False
        
def CFR_verificar_3velas_resistencia(par):

    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False

def VFR_verificar_3velas_martillo_rojo_resistencia(velas,lista_pares,i):
    nro = len(velas)
    if nro < 3:
        print(nro)   

    if nro > 3:
        if velas[nro-7][8] == "martillo_rojo" or velas[nro-6][8] == "martillo_rojo" or velas[nro-5][8] == "martillo_rojo" or velas[nro-4][8] == "martillo_rojo" or velas[nro-3][8] == "martillo_rojo" or velas[nro-2][8] == "martillo_rojo":
            return True
        else:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return False
    return False
        
def CFR_verificar_3velas_martillo_rojo_resistencia(par):

    lista_pares = pd.read_csv("pares3.csv")
    i = 0
    while(lista_pares['par'][i] != "END"):
        if par == lista_pares['par'][i]:
            lista_pares.loc[i,'tp'] = 13
            lista_pares.loc[i,'sl'] = 0
            lista_pares.to_csv("pares3.csv",index=False)
            return True
        i = i + 1
    return False


def inicializar_pares3():

    i = 0
    lista_pares = pd.read_csv("pares3.csv")

    while(lista_pares['par'][i] != "END"):
        lista_pares.loc[i,'tp'] = 13
        lista_pares.loc[i,'sl'] = 0
        i = i + 1

    lista_pares['tp'] = lista_pares['tp'].astype(int)
    lista_pares['sl'] = lista_pares['sl'].astype(int)
    lista_pares.to_csv("pares3.csv",index=False)

def inicializar_pares2():

    i = 0
    lista_pares = pd.read_csv("pares2.csv")

    while(lista_pares['par'][i] != "END"):
        lista_pares.loc[i,'tp'] = 0.0
        lista_pares.loc[i,'sl'] = 0.0
        i = i + 1

    lista_pares['tp'] = lista_pares['tp'].astype(float)
    lista_pares['sl'] = lista_pares['sl'].astype(float)
    lista_pares.to_csv("pares2.csv",index=False)


def tendencia_par(par,intervalo,nro_velas):
    datos_vela = [par,intervalo,nro_velas]
    velas = leer_vela(datos_vela)
    if velas[nro_velas-1][7] == "verde" and velas[nro_velas-2][7] == "verde":
        tendencia_par = "subida"
        return tendencia_par
    elif velas[nro_velas-1][7] == "roja" and velas[nro_velas-2][7] == "roja":
        tendencia_par = "bajada"
        return tendencia_par
    else:
        tendencia_par = "neutra"
        return tendencia_par
    
def obtener_rsi_old(velas,pos_vela,periodo):
    periodos = periodo
    i = 0
    SumOfGains = 0
    SumOfLosses = 0
    while i < periodos:
        if velas[pos_vela - i][7] == "verde":
            ganancia = abs(float(velas[pos_vela - i][4]) - float(velas[pos_vela - i][1]))
            SumOfGains = SumOfGains + ganancia
        else:
            perdida = abs(float(velas[pos_vela - i][1]) - float(velas[pos_vela - i][4]))
            SumOfLosses = SumOfLosses + perdida
        i = i + 1
    AverageGain = SumOfGains / periodos
    AverageLoss = SumOfLosses / periodos
    rs = AverageGain / AverageLoss
    rsi = round(100 - (100 / (1 + rs)),2)
    return rsi


def calculate_rsi(data, window):
    """
    Calculate the Relative Strength Index (RSI) for a given dataset.

    Parameters:
        data (pd.Series): A pandas Series of prices (e.g., closing prices).
        window (int): The lookback period for RSI calculation (default is 14).

    Returns:
        pd.Series: A pandas Series containing the RSI values.
    """
    # Calculate price changes
    delta = data.diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate the average gain and loss
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    # Calculate the Relative Strength (RS)
    rs = avg_gain / avg_loss

    # Calculate the RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi

def obtener_rsi(velas,pos_vela,periodo):
    # Example usage
    # Assuming you have a DataFrame `df` with a 'Close' column
    p14 = float(velas[pos_vela][4])
    p13 = float(velas[pos_vela-1][4])
    p12 = float(velas[pos_vela-2][4])
    p11 = float(velas[pos_vela-3][4])
    p10 = float(velas[pos_vela-4][4])
    p09 = float(velas[pos_vela-5][4])
    p08 = float(velas[pos_vela-6][4])
    p07 = float(velas[pos_vela-7][4])
    p06 = float(velas[pos_vela-8][4])
    p05 = float(velas[pos_vela-9][4])
    p04 = float(velas[pos_vela-10][4])
    p03 = float(velas[pos_vela-11][4])
    p02 = float(velas[pos_vela-12][4])
    p01 = float(velas[pos_vela-13][4])
    p00 = float(velas[pos_vela-14][4])
    df = pd.DataFrame({'Close': [p00, p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14]})
    df['RSI'] = calculate_rsi(df['Close'],int(periodo))
    
    rsi_value = df.at[14, 'RSI']
    return rsi_value

def obtener_ema9(velas,pos_vela):
    p09 = float(velas[pos_vela][4])
    p08 = float(velas[pos_vela-1][4])
    p07 = float(velas[pos_vela-2][4])
    p06 = float(velas[pos_vela-3][4])
    p05 = float(velas[pos_vela-4][4])
    p04 = float(velas[pos_vela-5][4])
    p03 = float(velas[pos_vela-6][4])
    p02 = float(velas[pos_vela-7][4])
    p01 = float(velas[pos_vela-8][4])
    p00 = float(velas[pos_vela-9][4])

    # Example data (replace with your actual data)
    data = {'Price': [p00, p01, p02, p03, p04, p05, p06, p07, p08, p09]}
    df = pd.DataFrame(data)

    # Calculate the 9-period EMA
    df['EMA_9'] = df['Price'].ewm(span=9, adjust=False).mean()
    
    ema9_value = df.at[9, 'EMA_9']

    return ema9_value


def obtener_ema20(velas,pos_vela):
    p20 = float(velas[pos_vela][4])
    p19 = float(velas[pos_vela-1][4])
    p18 = float(velas[pos_vela-2][4])
    p17 = float(velas[pos_vela-3][4])
    p16 = float(velas[pos_vela-4][4])
    p15 = float(velas[pos_vela-5][4])
    p14 = float(velas[pos_vela-6][4])    
    p13 = float(velas[pos_vela-7][4])
    p12 = float(velas[pos_vela-8][4])
    p11 = float(velas[pos_vela-9][4])
    p10 = float(velas[pos_vela-10][4])
    p09 = float(velas[pos_vela-11][4])
    p08 = float(velas[pos_vela-12][4])
    p07 = float(velas[pos_vela-13][4])
    p06 = float(velas[pos_vela-14][4])
    p05 = float(velas[pos_vela-15][4])
    p04 = float(velas[pos_vela-16][4])
    p03 = float(velas[pos_vela-17][4])
    p02 = float(velas[pos_vela-18][4])
    p01 = float(velas[pos_vela-19][4])
    p00 = float(velas[pos_vela-20][4])

    # Example data (replace with your actual data)
    data = {'Price': [p00, p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20]}
    df = pd.DataFrame(data)

    # Calculate the 9-period EMA
    df['EMA_20'] = df['Price'].ewm(span=20, adjust=False).mean()
    ema20_value = df.at[20, 'EMA_20']

    return df

def obtener_ema(velas,pos_vela,eman):
    
    p = float(velas[pos_vela-eman][4])
    data = {'Price': [p]}
    df = pd.DataFrame(data)
    
    
    for i in range(1, eman + 1,1):
        # Create a new row as a DataFrame
        
        p = float(velas[pos_vela - eman + i][4])
        new_row = pd.DataFrame({'Price': [p]})

        # Concatenate the new row
        df = pd.concat([df, new_row], ignore_index=True)
     
    df['EMA'] = df['Price'].ewm(span=eman, adjust=False).mean()
    ema_value = df.at[eman, 'EMA']   
       
    return ema_value
        

