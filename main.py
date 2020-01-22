from flask import Flask, request
import requests, os
import blueprint2json
from gevent.pywsgi import WSGIServer
import parser

app = Flask(__name__)

@app.route('/parse', methods = ['POST'])
def parse():
    body = request.get_json()
    ansibles = parser.parse_data(body["name"], body["data"])

    print('Reading Ansible files ---------')
    for url in ansibles:
        print('Reading   %s ------- '%url)
        temp = str(url).split('/')
        filename = temp[-1]
        foldername = os.path.join(*temp[4:-1])
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        outfile = open(os.path.join(foldername, filename), "w")
        outfile.write(str(requests.get(url).content))
        print('Ansible files done ------- ')
        print('blueprint2json ongoing ------- ')
        os.system('python3 blueprint2json.py a test2.yml > Tosca_ansible.json')
    return "OK"

if __name__ == '__main__':
    http_server = WSGIServer(('', 80), app)
    http_server.serve_forever()
