import requests
import pprint
import json

host='localhost'
port=9696

query_string = 'http://' + host + ':' + str(port) + '/v2.0/ports'
print('query string', query_string)
all_ports = requests.get(query_string)
ports_json = json.loads(all_ports.text)
port_list = ports_json['ports']
for x in port_list:
    print '-'*20
    print x

#pprint.pprint(all_ports.text)
