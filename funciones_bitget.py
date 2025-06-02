#importando modulo para hacer POST y GET
import requests
#importando las claves secretas bitget del modulo pi_secret_keys
from api_secret_keys import apiKey,passphrase
from HDMAC_Sign_Post import get_timestamp,get_sign

#importando modulo para hacer search en strings
import re

#importando modulo para trabajar con csv
import pandas as pd

def crear_monto_en_la_meneda_comprada(precio,apalancamiento,monto):
    if precio != 0:
        resultado = (monto/precio)*apalancamiento
        resultado_str = str(resultado)
        return resultado_str
    else:
        return "0"


def obtener_orderId(datos):
    datos_str = str(datos)
    datos_lista = datos_str.split('"')
    return datos_lista[25]

#extrayendo valores del mensaje al setear order
def status_order(datos):
    status_order_list =list()
    datos_str = str(datos)
    datos_lista = datos_str.split('"')
    status_order_list.append(datos_lista[7])
    status = datos_lista[7] 
    if status == "success":
        status_order_list.append(datos_lista[15])
        status_order_list.append(datos_lista[19])
    else:
        status_order_list.append("")
        status_order_list.append("")  
    return status_order_list

#extrayendo valores del mensaje al setear leverage
def status_leverage(datos, tipo):
    status_leverage_list =list()
    datos_str = str(datos)
    datos_lista = datos_str.split('"')
    status_leverage_list.append(datos_lista[7])
    status = datos_lista[7] 
    if status == "success":
        status_leverage_list.append(datos_lista[15])
        if (tipo == "buy"):
            status_leverage_list.append(datos_lista[21])
            status_leverage_list.append(datos_lista[23])
        else:
            status_leverage_list.append(datos_lista[25])
            status_leverage_list.append(datos_lista[27])
        status_leverage_list.append(datos_lista[35])
    else:
        status_leverage_list.append("")
        status_leverage_list.append("")
        status_leverage_list.append("")
        status_leverage_list.append("")
    return status_leverage_list

#extrayendo valores del mensaje al setear margin
def status_margin(datos):
    status_magin_list =list()
    datos_str = str(datos)
    datos_lista = datos_str.split('"')
    status_magin_list.append(datos_lista[7])
    status = datos_lista[7] 
    if status == "success":
        status_magin_list.append(datos_lista[15])
        status_magin_list.append(datos_lista[31])
    else:
        status_magin_list.append("")
        status_magin_list.append("")
    return status_magin_list

#crear orden
def crear_orden(param_list):
    url_bitget_set_margin_mode = "https://api.bitget.com/api/v2/mix/account/set-margin-mode"
    request_path_margin_mode = "/api/v2/mix/account/set-margin-mode"
    url_bitget_set_leverage = "https://api.bitget.com/api/v2/mix/account/set-leverage"
    request_path_leverage = "/api/v2/mix/account/set-leverage"
    url_bitget_start_order = "https://api.bitget.com/api/v2/mix/order/place-order"
    request_path_start_order = "/api/v2/mix/order/place-order"
    #desempaquetando lista
    par,porx,usdt_monto,tipo,tp,sl = param_list
    prize = obtener_precio_par(par)
    monto = crear_monto_en_la_meneda_comprada(float(prize),float(porx),float(usdt_monto))
    
    #haciendo el POST al url the bitget para setear margin mode
    json_data = {
        'symbol': par,
        'productType': 'usdt-futures',
        'marginCoin': 'USDT',
        'marginMode': 'isolated',
    }
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(json_data,request_path_margin_mode,"POST")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    
    response = requests.post(url_bitget_set_margin_mode, headers=headers, json=json_data)
    
    #lista_status_margin = status_margin(response.content)
    
   
    
    #haciendo el POST al url the bitget para setaer levarege
    if (tipo == "buy"):
        tipo2 = "long"
    else:
        tipo2 = "short"
        
    json_data = {
        'symbol': par,
        'productType': 'usdt-futures',
        'marginCoin': 'USDT',
        'leverage': porx,
        'holdSide': tipo2,
    }
    
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(json_data,request_path_leverage,"POST")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    
    response = requests.post(url_bitget_set_leverage, headers=headers, json=json_data)
    #lista_status_leverage = status_leverage(response.content,tipo)
    
    
    #haciendo el POST al url the bitget para crear orden
    json_data = {
        'symbol': par,
        'productType': 'usdt-futures',
        'marginMode': 'isolated',
        'marginCoin': 'USDT',
        'size': monto,
        #'price': prize,
        'side': tipo,
        'tradeSide': 'open',
        'orderType': 'market',
        'presetStopSurplusPrice': tp,
        'presetStopLossPrice': sl,
    }
    
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(json_data,request_path_start_order,"POST")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    
    response = requests.post(url_bitget_start_order, headers=headers, json=json_data)
    #lista_status_order = status_order(response.content)
    
    
#extrayendo valores de lectura de la orden abiierta para cambiar tp y sl
def status_gettpsl(datos):
    status_gettpsl_list =list()
    datos_str = str(datos)
    datos_lista = datos_str.split('"')
    status = datos_lista[7]
    status2 = ""
    if status == "success":
        status2 = datos_lista[14]
    if status == "success" and status2 != ":null,":
        status_gettpsl_list.append(datos_lista[7])
        status_gettpsl_list.append(datos_lista[17])
        status_gettpsl_list.append(datos_lista[21])
        status_gettpsl_list.append(datos_lista[25])
        status_gettpsl_list.append(datos_lista[29])
        status_gettpsl_list.append(datos_lista[41])
        status_gettpsl_list.append(datos_lista[53])
        status_gettpsl_list.append(datos_lista[77])
        status_gettpsl_list.append(datos_lista[81])
        status_gettpsl_list.append(datos_lista[105])
        status_gettpsl_list.append(datos_lista[109])
    else:
        if status2 == ":null,":
            status_gettpsl_list.append("Not Open")  
        else:
            status_gettpsl_list.append(datos_lista[7])          
        status_gettpsl_list.append("")
        status_gettpsl_list.append("")
        status_gettpsl_list.append("")
        status_gettpsl_list.append("") 
        status_gettpsl_list.append("")
        status_gettpsl_list.append("") 
        status_gettpsl_list.append("")
        status_gettpsl_list.append("") 
        status_gettpsl_list.append("")
        status_gettpsl_list.append("")  
        
    return status_gettpsl_list

#extrayendo valores del seteo de cambiar tp sl
def status_settpsl(datos):
    status_settpsl_list =list()
    datos_str = str(datos)
    datos_lista = datos_str.split('"')
    status_settpsl_list.append(datos_lista[7])
    status = datos_lista[7] 
    if status == "success":
        status_settpsl_list.append(datos_lista[15])
        status_settpsl_list.append(datos_lista[19])
    else:
        status_settpsl_list.append("")
        status_settpsl_list.append("")
    return status_settpsl_list
    
#cambiar Take Profit y Stop Lost
def cambiar_tpsl(param_list):
    url_bitget_order_pending = "https://api.bitget.com/api/v2/mix/order/orders-pending"
    request_path_order_pending = "/api/v2/mix/order/orders-pending"
    url_bitget_modify_order = "https://api.bitget.com/api/v2/mix/order/modify-order"
    request_path_modify_order = "/api/v2/mix/order/modify-order"
    
    #desempaquetando lista
    par,tp,sl = param_list
    
    
    #haciendo el GET al url the bitget para obtener datos de la orden (orderId
    # Need to be sorted in ascending alphabetical order by key
    params = {
        'productType': 'usdt-futures',
        'symbol': par,
    }
        
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(params,request_path_order_pending,"GET")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    response = requests.get(url_bitget_order_pending, headers=headers, params=params)
    lista_status_gettpsl = status_gettpsl(response.content)
    
    
    #obtener orderId
    if lista_status_gettpsl[0] == "success":
        orderId = obtener_orderId(response.content)
    
        #haciendo el POST al url the bitget para cambiat Take Profit y Stop Lost
        json_data = {
            'orderId': orderId,
            'symbol': par,
            'productType': 'usdt-futures',
            'newClientOid': orderId,
            'newPresetStopSurplusPrice': tp,
            'newPresetStopLossPrice': sl,
        }
        #creando timestamp y sign
        timestamp = get_timestamp()
        sign = get_sign(json_data,request_path_modify_order,"POST")
    
        headers = {
            'ACCESS-KEY': apiKey,
            'ACCESS-SIGN': sign,
            'ACCESS-PASSPHRASE': passphrase,
            'ACCESS-TIMESTAMP': str(timestamp),
            'locale': 'en-US',
            'Content-Type': 'application/json',
        }
    
        response = requests.post(url_bitget_modify_order, headers=headers, json=json_data)
        #lista_status_settpsl = status_settpsl(response.content)
        
    
#cancelar orden
def cancel_order(param_list):
    url_bitget_order_pending = "https://api.bitget.com/api/v2/mix/order/orders-pending"
    request_path_order_pending = "/api/v2/mix/order/orders-pending"
    url_bitget_order_cancel = "https://api.bitget.com/api/v2/mix/order/cancel-order"
    request_path_order_cancel = "/api/v2/mix/order/cancel-order"
    
    #desempaquetando lista
    par = param_list
    
    #haciendo el GET al url the bitget para obtener datos de la orden
    # Need to be sorted in ascending alphabetical order by key
    params = {
        'productType': 'usdt-futures',
        'symbol': par,
    }
    
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(params,request_path_order_pending,"GET")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    response = requests.get(url_bitget_order_pending, headers=headers, params=params)
    lista_status_gettpsl = status_gettpsl(response.content)
    
    #obtener orderId
    if lista_status_gettpsl[0] == "success":
        orderId = obtener_orderId(response.content)
        #haciendo el POST al url the bitget para cancelar orden
        json_data = {
            'orderId': orderId,
            'symbol': par,
            'productType': 'usdt-futures',
        }
        #creando timestamp y sign
        timestamp = get_timestamp()
        sign = get_sign(json_data,request_path_order_cancel,"POST")
    
        headers = {
            'ACCESS-KEY': apiKey,
            'ACCESS-SIGN': sign,
            'ACCESS-PASSPHRASE': passphrase,
            'ACCESS-TIMESTAMP': str(timestamp),
            'locale': 'en-US',
            'Content-Type': 'application/json',
        }
    
        response = requests.post(url_bitget_order_cancel, headers=headers, json=json_data)
        #lista_status_settpsl = status_settpsl(response.content)
        

#extrayendo valores del mensaje de cancelar possicion
def status_cancepos(datos):
    status_cancepos_list =list()
    datos_str = str(datos)
    datos_lista = datos_str.split('"')
    status_cancepos_list.append(datos_lista[7])
    status = datos_lista[7] 
    if status == "success":
        status_cancepos_list.append(datos_lista[17])
        status_cancepos_list.append(datos_lista[21])
    else:
        status_cancepos_list.append("")
        status_cancepos_list.append("")
    return status_cancepos_list
        
    
def cancel_position(param_list):
    url_bitget_close_positions = "https://api.bitget.com/api/v2/mix/order/close-positions"
    request_path_close_positions = "/api/v2/mix/order/close-positions"
    
    #desempaquetando lista
    par = param_list
    
    
    #haciendo el POST al url the bitget para cancelar orden
    json_data = {
        'symbol': par,
        'productType': 'usdt-futures',
    }
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(json_data,request_path_close_positions,"POST")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    
    response = requests.post(url_bitget_close_positions, headers=headers, json=json_data)
    #lista_status_cancepos = status_cancepos(response.content)
    
    
def cambiar_tpsl_position(param_list):
    print("hola")

def verificar_si_orden_abierta(param_list):
    url_bitget_order_pending = "https://api.bitget.com/api/v2/mix/order/orders-pending"
    request_path_order_pending = "/api/v2/mix/order/orders-pending"
    
    #desempaquetando lista
    par = param_list
    
    #haciendo el GET al url the bitget para obtener datos de la orden
    # Need to be sorted in ascending alphabetical order by key
    params = {
        'productType': 'usdt-futures',
        'symbol': par,
    }
    
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(params,request_path_order_pending,"GET")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    response = requests.get(url_bitget_order_pending, headers=headers, params=params)
    lista_status_gettpsl = status_gettpsl(response.content)
    
    
    if lista_status_gettpsl[0] != "success":
        return False    
    else:
        return True 

def status_openpos(datos):
    status_openpos_list =list()
    datos_str = str(datos)
    datos_lista = datos_str.split('"')
    status = datos_lista[7]
    status2 = datos_lista[12]
    if status == "success" and status2 != ":[]}'":
        status_openpos_list.append(datos_lista[7])
        status_openpos_list.append(datos_lista[15])
        status_openpos_list.append(datos_lista[19])
        status_openpos_list.append(datos_lista[23])
        status_openpos_list.append(datos_lista[31])
        status_openpos_list.append(datos_lista[43])
        status_openpos_list.append(datos_lista[47])
        status_openpos_list.append(datos_lista[55])
        status_openpos_list.append(datos_lista[59])
        status_openpos_list.append(datos_lista[67])
        status_openpos_list.append(datos_lista[71])
        status_openpos_list.append(datos_lista[79])
    else:
        status_openpos_list.append("NOT OPEN")          
        status_openpos_list.append("")
        status_openpos_list.append("")
        status_openpos_list.append("")
        status_openpos_list.append("") 
        status_openpos_list.append("")
        status_openpos_list.append("") 
        status_openpos_list.append("")
        status_openpos_list.append("") 
        status_openpos_list.append("")
        status_openpos_list.append("")  
        status_openpos_list.append("") 
        
    return status_openpos_list
    

def verificar_si_posicion_abierta(param_list):
    url_bitget_get_positions = "https://api.bitget.com/api/v2/mix/position/single-position"
    request_path_get_positions = "/api/v2/mix/position/single-position"
    
    #desempaquetando lista
    par = param_list
    
    #haciendo el GET al url the bitget para obtener datos de la orden
    # Need to be sorted in ascending alphabetical order by key
    params = {
        'marginCoin': 'USDT',
        'productType': 'usdt-futures',
        'symbol': par,
    }
    
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(params,request_path_get_positions,"GET")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.get(url_bitget_get_positions, headers=headers, params=params)
        lista_status_openpos = status_openpos(response.content)
    except Exception as e:
        return False
    else:
        if lista_status_openpos[0] != "success":
            return False    
        else:
            return True 

def obtener_unprofit_posicion(param_list):
    url_bitget_get_positions = "https://api.bitget.com/api/v2/mix/position/single-position"
    request_path_get_positions = "/api/v2/mix/position/single-position"
    
    #desempaquetando lista
    par = param_list
    
    #haciendo el GET al url the bitget para obtener datos de la orden
    # Need to be sorted in ascending alphabetical order by key
    params = {
        'marginCoin': 'USDT',
        'productType': 'usdt-futures',
        'symbol': par,
    }
    
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(params,request_path_get_positions,"GET")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    try:
        response = requests.get(url_bitget_get_positions, headers=headers, params=params)
        lista_status_openpos = status_openpos(response.content)
    
    except Exception as e:
        return "error"
    else:
        if lista_status_openpos[0] != "success":
            return "error"   
        else:
            roe = 100 * (float(lista_status_openpos[9]) / float(lista_status_openpos[4]))
            return str(roe)

def crear_orden_trial(param_list):
    url_bitget_set_margin_mode = "https://api.bitget.com/api/v2/mix/account/set-margin-mode"
    request_path_margin_mode = "/api/v2/mix/account/set-margin-mode"
    url_bitget_set_leverage = "https://api.bitget.com/api/v2/mix/account/set-leverage"
    request_path_leverage = "/api/v2/mix/account/set-leverage"
    url_bitget_Trigger_order = "https://api.bitget.com/api/v2/mix/order/place-plan-order"
    request_path_Trigger_order = "/api/v2/mix/order/place-plan-order"
    #desempaquetando lista
    par,porx,usdt_monto,tipo,tp,sl = param_list
    
    prize = obtener_precio_par(par)
    
    monto = crear_monto_en_la_meneda_comprada(float(prize),float(porx),float(usdt_monto))
    
    monto2 = float(monto)
    monto2 = round(monto2,3)
    monto = str(monto2)

    #haciendo el POST al url the bitget para setear margin mode
    json_data = {
        'symbol': par,
        'productType': 'usdt-futures',
        'marginCoin': 'USDT',
        'marginMode': 'isolated',
    }
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(json_data,request_path_margin_mode,"POST")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    
    response = requests.post(url_bitget_set_margin_mode, headers=headers, json=json_data)
    
    lista_status_margin = status_margin(response.content)
    
    
    
    #haciendo el POST al url the bitget para setaer levarege
    if (tipo == "buy"):
        tipo2 = "long"
    else:
        tipo2 = "short"
        
    json_data = {
        'symbol': par,
        'productType': 'usdt-futures',
        'marginCoin': 'USDT',
        'leverage': porx,
        'holdSide': tipo2,
    }
    
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(json_data,request_path_leverage,"POST")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    
    response = requests.post(url_bitget_set_leverage, headers=headers, json=json_data)
    #lista_status_leverage = status_leverage(response.content,tipo)
    
    
    #haciendo el POST al url the bitget para crear orden
    json_data = {
        'planType': 'track_plan',
        'symbol': par,
        'productType': 'usdt-futures',
        'marginMode': 'isolated',
        'marginCoin': 'USDT',
        'size': monto,
        'callbackRatio': '0.01',
        'triggerPrice': prize,
        'triggerType': 'mark_price',
        'side': tipo,
        'tradeSide': 'open',
        'orderType': 'market',
        #'stopSurplusTriggerPrice': tp,
        'stopLossExecutePrice': sl,
    }
    
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(json_data,request_path_Trigger_order,"POST")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    
    response = requests.post(url_bitget_Trigger_order, headers=headers, json=json_data)
    print(response.content)
    code = obtener_codigo_erro_trial_order(response.content)
    print(code)
    i = 1
    while code == "40808":
        prize = obtener_precio_par(par)
        monto = crear_monto_en_la_meneda_comprada(float(prize),float(porx),float(usdt_monto))
        monto2 = float(monto)
        monto2 = round(monto2,3-i)
        monto = str(monto2)
        i = i + 1
        #haciendo el POST al url the bitget para crear orden
        json_data = {
            'planType': 'track_plan',
            'symbol': par,
            'productType': 'usdt-futures',
            'marginMode': 'isolated',
            'marginCoin': 'USDT',
            'size': monto,
            'callbackRatio': '0.01',
            'triggerPrice': prize,
            'triggerType': 'mark_price',
            'side': tipo,
            'tradeSide': 'open',
            'orderType': 'market',
            #'stopSurplusTriggerPrice': tp,
            'stopLossExecutePrice': sl,
        }
    
        #creando timestamp y sign
        timestamp = get_timestamp()
        sign = get_sign(json_data,request_path_Trigger_order,"POST")
    
        headers = {
            'ACCESS-KEY': apiKey,
            'ACCESS-SIGN': sign,
            'ACCESS-PASSPHRASE': passphrase,
            'ACCESS-TIMESTAMP': str(timestamp),
            'locale': 'en-US',
            'Content-Type': 'application/json',
        }
    
        response = requests.post(url_bitget_Trigger_order, headers=headers, json=json_data)
        #print(response.content)
        #code = obtener_codigo_erro_trial_order(response.content)
        #print(code)
    
    """"
    lista_status_order = status_order(response.content)
    print("----------")
    print("Datos del Seteo de la orden")
    print(f"Status: {lista_status_order[0]}")
    print(f"clientOid: {lista_status_order[1]}")
    print(f"orderId: {lista_status_order[2]}")
    """
    
def obtener_codigo_erro_trial_order(datos):
    status_price_list =list()
    datos_str = str(datos)
    datos_lista = datos_str.split('"')
    return datos_lista[3]
    
def obtener_precio_par(param_list):
    url_bitget_market_Price = "https://api.bitget.com/api/v2/mix/market/symbol-price"
    request_path_market_Price = "/api/v2/mix/market/symbol-price"
    
    
    #desempaquetando lista
    par = param_list
    
    #haciendo el GET al url the bitget para obtener datos de la orden
    # Need to be sorted in ascending alphabetical order by key
    params = {
        'productType': 'usdt-futures',
        'symbol': par,
    }
    
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(params,request_path_market_Price,"GET")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    response = requests.get(url_bitget_market_Price, headers=headers, params=params)
    lista_status_price = status_price(response.content)
   
    if lista_status_price[0] == "success":
        return lista_status_price[2]
    else:
        return "0"

def status_price(datos):
    status_price_list =list()
    datos_str = str(datos)
    datos_lista = datos_str.split('"')
    status = datos_lista[7]
    if status == "success":
        status_price_list.append(datos_lista[7])
        status_price_list.append(datos_lista[15])
        status_price_list.append(datos_lista[19])
    else:
        status_price_list.append(datos_lista[7])        
        status_price_list.append("")
        status_price_list.append("")
                
    return status_price_list

#atribuir intervalo
def atribuir_intervalo(inter):
    if inter == "0":
        return "30m"
    if inter == "1":
        return "1H"
    if inter == "2":
        return "6H"
    if inter == "3":
        return "12Hutc"
    if inter == "4":
        return "1Dutc"
    if inter == "5":
        return "1Dutc"


#estraer datos de lista bruta
def estraer_datos_vela(data):
    vela = list()
    datos_str = str(data)
    datos_lista_split = datos_str.split(',')
    for datos_lista_split_values in datos_lista_split:
        lista_datos_estraidos = datos_lista_split_values.split('"')
        i = 0
        for values in lista_datos_estraidos:
            if i == 1:
                vela.append(str(values))
            i = i + 1
    vela.append("SinColor")
    vela.append("SinTipo")
    if float(vela[1]) < float(vela[4]):
        vela[7] = "verde"
    else:
        vela[7] = "roja"
    
    return vela

#Crear lista de velas
def crear_lista_velas(data,nro):
    velas_array = list()
    datos_str = str(data)
    datos_lista_bruto = datos_str.split('[')
    i = 0
    for data in datos_lista_bruto:
        if i > 1:
            datos_extraidos = estraer_datos_vela(data) 
            velas_array.append(datos_extraidos)
        i = i + 1
   
    return velas_array
              

#leer vela
def leer_vela(param_list):
    url_bitget_mix_market_candle = "https://api.bitget.com/api/v2/mix/market/candles"
    request_path_mix_market_candle = "/api/v2/mix/market/candles"
 
    #desempaquetando lista
    par,inter,nro_velas = param_list
    
    intervalo = atribuir_intervalo(inter)
    
    #haciendo el GET al url the bitget para obtener datos de la orden (orderId
    # Need to be sorted in ascending alphabetical order by key
    params = {
        'granularity': intervalo,
        'limit': nro_velas,
        'productType': 'usdt-futures',
        'symbol': par,        
    }
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(params,request_path_mix_market_candle,"GET")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    try:
        response = requests.get(url_bitget_mix_market_candle, headers=headers, params=params)
        velas_array = crear_lista_velas(response.content,nro_velas)
    except Exception as e:
        velas_array = []
    else:
        velas_array = crear_lista_velas(response.content,nro_velas)
    return velas_array


def get_lista_all_posiciones(datos):
    lista = list()
    lista_pares = pd.read_csv("pares2.csv")
    datos_str = str(datos)
    i = 0
    while(lista_pares['par'][i] != "END"):
        par = lista_pares['par'][i]
        par2 = f'"{par}"'
        resultado = re.search(par2,datos_str)
        resultado_str = str(resultado)
        if resultado_str != "None":
            lista.append(par)
            
        i = i + 1    
    return lista

def lista_de_posiciones_abiertas():
    url_bitget_get_allpositions = "https://api.bitget.com/api/v2/mix/position/all-position"
    request_path_get_allpositions = "/api/v2/mix/position/all-position"
    
    #desempaquetando lista
    #par = param_list
    
    #haciendo el GET al url the bitget para obtener datos de la orden
    # Need to be sorted in ascending alphabetical order by key
    params = {
        'marginCoin': 'USDT',
        'productType': 'usdt-futures',
    }
    
    #creando timestamp y sign
    timestamp = get_timestamp()
    sign = get_sign(params,request_path_get_allpositions,"GET")
    
    headers = {
        'ACCESS-KEY': apiKey,
        'ACCESS-SIGN': sign,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': str(timestamp),
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(url_bitget_get_allpositions, headers=headers, params=params)
        lista_all_position = get_lista_all_posiciones(response.content)
    except Exception as e:
        lista_all_position = [] 
        print(lista_all_position)
        print(lista_all_position)
        print(lista_all_position)
        print(lista_all_position)
    else:
        lista_all_position = get_lista_all_posiciones(response.content)
    return lista_all_position

    #response = requests.get(url_bitget_get_allpositions, headers=headers, params=params)
    
    #lista_all_position = get_lista_all_posiciones(response.content)

    #return lista_all_position

    """"
    lista_status_openpos = status_openpos(response.content)
    
    if lista_status_openpos[0] != "success":
        return False    
    else:
        return True
    """