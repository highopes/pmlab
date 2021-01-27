import requests
import urllib3
from time import sleep

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "http://10.75.53.41:8080/webui/#/dashboard"

payload = {}
headers = {
    'Accept': 'application/yang-data+json',
    'Authorization': 'Basic Y2lzY286Y2lzY28=',
    'Cookie': 'Auth=cisco:1611572189:469f62d97653a8763b63b3d7458c7622ff78f451a23e3a073c0315fb2eaa0a10548b1b260ac4cb7c7e967b4e32d09e6b2eba3f6b3bdaa9bd20bb89b61012f49dfc6b7ff51cd165e53631b9671b2780e7f9af5fca8a846a3d48e1d8bdf0efc9ad:f6b00ac2d7fb39f03d224144a8871b162405363ebc80f14a3cd93a4ddecfba10'
}
while True:
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        print(response.text)
        sleep(1)
    except KeyboardInterrupt:
        break

