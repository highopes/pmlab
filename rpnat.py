import requests
import json

"""
Script to replace nat entry with a new one, it's useful when we need to replace nat entry frequently for kubernetes to 
expose its service in ACI CNI environment
"""
# current available external IP address (on outside)
CUR_EX = "10.75.53.113"
# the new external service IP address it has changed (on inside)
NEW_LC = "172.16.2.10"

url = 'http://10.75.53.189/ins'
switchuser = 'admin'
switchpassword = 'cisco.123'

myheaders = {'content-type': 'application/json-rpc'}
payload = [
    {
        "jsonrpc": "2.0",
        "method": "cli",
        "params": {
            "cmd": "show ip nat translation",
            "version": 1
        },
        "id": 1
    }
]
response = requests.post(url, data=json.dumps(payload), headers=myheaders, auth=(switchuser, switchpassword)).json()

nat_entry_list = response["result"]["body"]["TABLE_nat_translation"]["ROW_nat_translation"]
print(nat_entry_list)

for nat_entry in nat_entry_list:
    if nat_entry["Inside_global_IP_V4_Address"] == CUR_EX:
        cur_lc = nat_entry["Inside_local_IP_V4_Address"]
        cmdstr = "no ip nat inside source static " + cur_lc + " " + CUR_EX
        # delete nat entry
        payload = [
            {
                "jsonrpc": "2.0",
                "method": "cli",
                "params": {
                    "cmd": "conf t",
                    "version": 1
                },
                "id": 1
            },
            {
                "jsonrpc": "2.0",
                "method": "cli",
                "params": {
                    "cmd": cmdstr,
                    "version": 1
                },
                "id": 2
            }
        ]
        response = requests.post(url, data=json.dumps(payload), headers=myheaders,
                                 auth=(switchuser, switchpassword)).json()
        print("Deleting Result:   \n")
        print(response)

cmdstr = "ip nat inside source static " + NEW_LC + " " + CUR_EX
payload = [
    {
        "jsonrpc": "2.0",
        "method": "cli",
        "params": {
            "cmd": "conf t",
            "version": 1
        },
        "id": 1
    },
    {
        "jsonrpc": "2.0",
        "method": "cli",
        "params": {
            "cmd": cmdstr,
            "version": 1
        },
        "id": 2
    }
]
response = requests.post(url, data=json.dumps(payload), headers=myheaders, auth=(switchuser, switchpassword)).json()
print("Add New Entry Result:   \n")
print(response)
