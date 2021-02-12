import json
import os
import uuid
import pathlib
import requests

from requests.exceptions import ConnectionError
from flask import Flask, request
from flask_wtf.csrf import CSRFProtect
from flask_swagger_ui import get_swaggerui_blueprint
from .iacparser import parse_data

AADM_TYPE = "AbstractApplicationDeploymentModel"

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
        return os.getenv("XOPERA_ENDPOINT", cls.config.get("XOPERA_ENDPOINT", "http://localhost"))

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

    @classmethod
    def get_xopera_api_key_header(cls):
        cls.init()
        api_key_header = os.getenv("XOPERA_API_KEY_HEADER", cls.config.get("XOPERA_API_KEY_HEADER", "X-API-Key"))
        return api_key_header       

csrf = CSRFProtect()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
#csrf.init_app(app)

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
    try:
        ansible_tuple = parse_data(outpath, body["data"])
    except Exception as e:
        return f"IaC Builder AADM parsing error {e}", 500        
    print('Downloading Ansible files ---------')
    download_dependencies(ansible_tuple[0], ansible_tuple[1], workpath)
    print('Ansible files done ------- ')
    print('Downloading Dependencies ---------')
    download_dependencies(ansible_tuple[2], ansible_tuple[3], workpath)
    print('Dependencies are done loading ------- ')
    print('blueprint2CSAR ongoing ------- ')
    files = prepare_files(body["name"], outpath)    
    return send_xopera_request(files, body["data"])


def prepare_files(name, outpath):
    os.system('python3 src/blueprint2CSAR.py %s %s --entry-definitions %s.yml --output %s' %
             (name, outpath[:outpath.rfind('/')], name, outpath))
    return [('CSAR', open('%s.zip' % (outpath,), 'rb'))]


def send_xopera_request(files, aadm_json):
    token = get_access_token(request)
    api_key = get_api_key(request)
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    elif api_key:
        headers = {XoperaConfig.get_xopera_api_key_header(): api_key}
    else:
        headers = None      

    params = {"project_domain": get_project_domain(aadm_json)}

    try:
        response = requests.post(XoperaConfig.get_xopera_api(), 
                                files=files,
                                params=params,
                                headers=headers,
                                verify=True)
                                
        return json.loads(response.text), response.status_code
    except ConnectionError as e:
        return f"IaC Builder Connection error to {XoperaConfig.get_xopera_api()}", 500    


def get_project_domain(json):
    for node in json.values():
        if isinstance(node, dict) and node.get("type") == AADM_TYPE and node.get("namespace"):
            return node.get("namespace")
    return None            


def get_access_token(request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
    try:
        auth_type, token = authorization.split(None, 1)
    except ValueError:
        return None
    if auth_type.lower() != "bearer":
        return None
    return token


def get_api_key(request):
    api_key = request.headers.get(XoperaConfig.get_xopera_api_key_header())
    if not api_key:
        return None
    return api_key    


def download_dependencies(urls, filenames, workpath):
    # TODO add access_token for download requests
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