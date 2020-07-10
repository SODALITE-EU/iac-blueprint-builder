from flask import Flask, request
import shutil
from flask_swagger_ui import get_swaggerui_blueprint
import requests
import os
import blueprint2json
from gevent.pywsgi import WSGIServer
import iacparser
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

with open('config.json') as config:
    config = json.load(config)
    XOPERA_ENDPOINT = config['X_OPERA_ENDPOINT']
    XOPERA_API = os.path.join(XOPERA_ENDPOINT, "manage")

print("starting with XOPERA endpoint:", XOPERA_API)


@app.route('/parse', methods=['POST'])
def parse():
    body = request.get_json()
    workpath = '%s-%d' % (body["name"], uuid.uuid1())
    if not os.path.exists(workpath):
        os.makedirs(workpath)
    outpath = os.path.join(workpath, body["name"])
    ansibles = iacparser.parse_data(outpath, body["data"])
    print('Reading Ansible files ---------')
    for url in ansibles:
        print('Reading   %s ------- ' % url)
        temp = str(url).split('/')
        filename = temp[-1]
        foldername = os.path.join(workpath, *temp[4:-1])
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        outfile = open(os.path.join(foldername, filename), "w")
        outfile.write(str(requests.get(url).text))
        outfile.close()
    print('Ansible files done ------- ')
    print('blueprint2CSAR ongoing ------- ')
    os.system('python3 src/blueprint2CSAR.py %s %s --entry-definitions %s.yml --output %s' %
              (body["name"], outpath[:outpath.rfind('/')], body["name"], outpath))
    files = [('CSAR', open('%s.zip' % (outpath,), 'rb'))]
    response = requests.post(XOPERA_API, files=files, verify=False)
    return json.loads(response.text)


if __name__ == '__main__':
    http_server = WSGIServer(('', 80), app)
    http_server.serve_forever()
