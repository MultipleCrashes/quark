import requests
import pprint
import json

host='localhost'
port=9696

get_query_string = 'http://' + host + ':' + str(port) + '/v2.0/ports'
print('get query string', get_query_string)
all_ports = requests.get(get_query_string)
ports_json = json.loads(all_ports.text)
port_list = ports_json['ports']
for x in port_list:
    print '-'*20
    # For list of ports , issue a delete request
    print 'deleting ', x['id']
    delete_port_query_string = 'http://' + host + ':' + str(port) +'/v2.0/ports/' + str(x['id'])
    delete_request = requests.delete(delete_port_query_string)
    print 'Delete response ->', delete_request.text

#pprint.pprint(all_ports.text)
