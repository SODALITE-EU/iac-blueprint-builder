import json
import os
import uuid

import requests
from flask import Flask, request
from flask_swagger_ui import get_swaggerui_blueprint
from gevent.pywsgi import WSGIServer

from src import iacparser

SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'
XOPERA_ENDPOINT_KEY = 'XOPERA_ENDPOINT'
XOPERA_ENDPOINT_DEFAULT = 'https://154.48.185.209'
CONFIG_PATH = 'config.json'

app = Flask(__name__)

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "SODALITE iac-blueprint-builder"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

XOPERA_ENDPOINT = os.getenv(XOPERA_ENDPOINT_KEY)

if not XOPERA_ENDPOINT:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as config:
            config = json.load(config)
            XOPERA_ENDPOINT = config[XOPERA_ENDPOINT_KEY]
    else:
        XOPERA_ENDPOINT = XOPERA_ENDPOINT_DEFAULT

XOPERA_API = os.path.join(XOPERA_ENDPOINT, "manage")

print("starting with XOPERA endpoint:", XOPERA_API)


@app.route('/parse', methods=['POST'])
def parse():
    body = request.get_json()
    workpath = '%s-%d' % (body["name"], uuid.uuid1())
    if not os.path.exists(workpath):
        os.makedirs(workpath)
    outpath = os.path.join(workpath, body["name"])
    ansible_tuple = iacparser.parse_data(outpath, body["data"])
    ansibles = ansible_tuple[0]
    ansible_paths = ansible_tuple[1]
    print('Downloading Ansible files ---------')
    for i, url in enumerate(ansibles):
        print('Reading   %s ------- ' % url)
        temp = str(url).split('/')
        filename = ansible_paths[i]
        foldername = os.path.join(workpath, *temp[4:-1])
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        outfile = open(os.path.join(foldername, filename), "w")
        outfile.write(str(requests.get(url).text))
        outfile.close()
    print('Ansible files done ------- ')
    depen_files = ansible_tuple[2]
    depen_paths = ansible_tuple[3]
    print('Downloading Dependencies ---------')
    for i, url in enumerate(depen_files):
        print('Reading   %s ------- ' % url)
        temp = str(url).split('/')
        filename = depen_paths[i]
        foldername = os.path.join(workpath, *temp[4:-1])
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        outfile = open(os.path.join(foldername, filename), "w")
        outfile.write(str(requests.get(url).text))
        outfile.close()
    print('Dependencies are done loading ------- ')
    print('blueprint2CSAR ongoing ------- ')
    os.system('python3 src/blueprint2CSAR.py %s %s --entry-definitions %s.yml --output %s' %
              (body["name"], outpath[:outpath.rfind('/')], body["name"], outpath))
    files = [('CSAR', open('%s.zip' % (outpath,), 'rb'))]
    response = requests.post(XOPERA_API, files=files, verify=False)
    return json.loads(response.text)


if __name__ == '__main__':
    http_server = WSGIServer(('', 80), app)
    http_server.serve_forever()
