import hmac
import base64
import json
import time
from api_secret_keys import secretKey


def get_timestamp():
  return int(time.time() * 1000)


def sign(message, secret_key):
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)


def pre_hash(timestamp, method, request_path, body):
  return str(timestamp) + str.upper(method) + request_path + body


def parse_params_to_str(params):
    params = [(key, val) for key, val in params.items()]
    params.sort(key=lambda x: x[0])
    from urllib.parse import urlencode
    url = '?' +urlencode(params);
    if url == '?':
        return ''
    return url


#if __name__ == '__main__':
API_SECRET_KEY = secretKey

def get_sign(json_data,request_path,post_get):
    timestamp = str(get_timestamp()) # get_timestamp()
    
    # POST GET
    if (post_get == "POST"):
      params = json_data
      body = json.dumps(params)
      sign2 = sign(pre_hash(timestamp, post_get, request_path, str(body)), API_SECRET_KEY)
      return sign2
    else:
      params = json_data
      body = ""
      request_path = request_path + parse_params_to_str(params) # Need to be sorted in ascending alphabetical order by key
      print(request_path)
      sign2 = sign(pre_hash(timestamp, post_get, request_path, str(body)), API_SECRET_KEY)
      print(sign2)
      return sign2