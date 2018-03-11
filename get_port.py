import requests
import pprint
import json
import threading

host='localhost'
port=9696
import thread

def get_and_delete_port():
    get_query_string = 'http://' + host + ':' + str(port) + '/v2.0/ports'
    print('get query string', get_query_string)
    all_ports = requests.get(get_query_string)
    ports_json = json.loads(all_ports.text)
    port_list = ports_json['ports']
    all_port_ids = []
    for x in port_list:
        # For list of ports , issue a delete request
        all_port_ids.append(x['id'])
    i = 1
    total_port_count = len(all_port_ids)
    while i < total_port_count:
        try:
            t = threading.Thread(target=delete_port, args = (all_port_ids[i:i+100],))
            t.start()
            i= i + 100
            print 'i ->', i
        except Exception as e:
            print('Unable to start thread -> ', str(e))


def delete_port(port_list):
    for ports in port_list:
        print 'Deleting port', ports
        delete_port_query_string = 'http://' + host + ':' + str(port) +'/v2.0/ports/' + ports
        delete_request = requests.delete(delete_port_query_string)
        print 'Delete Response Code -> ', delete_request.status_code

if __name__ == '__main__':
    get_and_delete_port()
