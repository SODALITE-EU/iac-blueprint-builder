from flask import Flask, request
import shutil
from flask_swagger_ui import get_swaggerui_blueprint
import requests, os
import blueprint2json
from gevent.pywsgi import WSGIServer
import parser
import uuid
import json
app = Flask(__name__)

SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "SODALITE iac-blueprint-builder"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


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
