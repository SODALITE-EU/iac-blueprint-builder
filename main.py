from flask import Flask, request
import shutil
import requests, os
import blueprint2json
from gevent.pywsgi import WSGIServer
import parser
import uuid
import json
app = Flask(__name__)

XOPERA_API = 'http://154.48.185.206:5000/manage'

@app.route('/parse', methods = ['POST'])
def parse():
    body = request.get_json()
    workpath = '%s-%d' % (body["name"], uuid.uuid1())
    if not os.path.exists(workpath):
        os.makedirs(workpath)
    outpath = os.path.join(workpath, body["name"])
    ansibles = parser.parse_data(outpath, body["data"])
    print('Reading Ansible files ---------')
    for url in ansibles:
        print('Reading   %s ------- '%url)
        temp = str(url).split('/')
        filename = temp[-1]
        foldername = os.path.join(workpath, *temp[4:-1])
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        outfile = open(os.path.join(foldername, filename), "w")
        outfile.write(str(requests.get(url).text))
        outfile.close()
    print('Ansible files done ------- ')
    print('blueprint2json ongoing ------- ')
    os.system('python3 blueprint2json.py %s %s.yml > %s.json' % (body["name"], outpath, outpath))
    payload = open('%s.json' % (outpath,), "r").read()
    shutil.rmtree(workpath)
    return json.loads(requests.post(XOPERA_API, json=json.loads(payload)).text)

if __name__ == '__main__':
    http_server = WSGIServer(('', 80), app)
    http_server.serve_forever()
