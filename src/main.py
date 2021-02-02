import json
import os
import uuid
import pathlib
import requests

from flask import Flask, request
from flask_wtf.csrf import CSRFProtect
from flask_swagger_ui import get_swaggerui_blueprint
from .iacparser import parse_data

class XoperaConfig:

    config_path = pathlib.Path(__file__).parent / pathlib.Path('../config_xopera.json')
    config = None

    @classmethod
    def init(cls):
        if cls.config is None:
            try:
                cls.config = json.load(cls.config_path.open())
            except:
                cls.config = {}    

    @classmethod
    def get_xopera_endpoint(cls):
        cls.init()
        return os.getenv("XOPERA_ENDPOINT", cls.config.get("XOPERA_ENDPOINT", "localhost"))

    @classmethod
    def get_xopera_swagger_url(cls):
        cls.init()
        swagger_url = os.getenv("SWAGGER_URL", cls.config.get("SWAGGER_URL", "/docs"))
        return swagger_url

    @classmethod
    def get_xopera_api_url(cls):
        cls.init()
        api_url = os.getenv("API_URL", cls.config.get("API_URL", "/static/swagger.json"))
        return api_url

    @classmethod
    def get_app_name(cls):
        cls.init()
        app_name = os.getenv("app_name", cls.config.get("app_name", "SODALITE iac-blueprint-builder"))
        return app_name

    @classmethod
    def get_xopera_api(cls):
        cls.init()
        manage_url = os.getenv("MANAGE_URL", cls.config.get("MANAGE_URL", "/manage"))
        return cls.get_xopera_endpoint() + manage_url

csrf = CSRFProtect()
app = Flask(__name__)
csrf.init_app(app)

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    XoperaConfig.get_xopera_swagger_url(),
    XoperaConfig.get_xopera_api_url(),
    config={
        'app_name': XoperaConfig.get_app_name()
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=XoperaConfig.get_xopera_swagger_url())

print("Starting with XOPERA endpoint:", XoperaConfig.get_xopera_api())

@app.route('/parse', methods=['POST'])
def parse():
    body = request.get_json()
    workpath = '%s-%d' % (body["name"], int(uuid.uuid1()))
    if not os.path.exists(workpath):
        os.makedirs(workpath)
    outpath = os.path.join(workpath, body["name"])
    ansible_tuple = parse_data(outpath, body["data"])
    print('Downloading Ansible files ---------')
    download_dependencies(ansible_tuple[0], ansible_tuple[1], workpath)
    print('Ansible files done ------- ')
    print('Downloading Dependencies ---------')
    download_dependencies(ansible_tuple[2], ansible_tuple[3], workpath)
    print('Dependencies are done loading ------- ')
    print('blueprint2CSAR ongoing ------- ')
    os.system('python3 src/blueprint2CSAR.py %s %s --entry-definitions %s.yml --output %s' %
              (body["name"], outpath[:outpath.rfind('/')], body["name"], outpath))
    files = [('CSAR', open('%s.zip' % (outpath,), 'rb'))]
    response = requests.post(XoperaConfig.get_xopera_api(), files=files, verify=True)
    return json.loads(response.text)

def download_dependencies(urls, filenames, workpath):
    for url, filename in zip(urls, filenames):
        print('Reading   %s ------- ' % url)
        temp = str(filename).split('/')
        foldername = os.path.join(workpath, *temp[:-1])
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        outfile = open(os.path.join(workpath, filename), "w")
        outfile.write(str(requests.get(url).text))
        outfile.close()

'''
if __name__ == '__main__':
    http_server = WSGIServer(('', 80), app)
    http_server.serve_forever()
'''