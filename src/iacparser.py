import yaml
import json
import re
import os 
import requests
import pathlib

from yaml import ScalarNode, CollectionNode, SequenceNode, MappingNode


class ModakConfig:
    
    config_path = pathlib.Path(__file__).parent / pathlib.Path('../config_modak.json')
    config = None

    valid_container_image_properties = ["image", "image_name", "container_runtime"]

    exec_node_requirements = ["application", "host", "runtime"]

    @classmethod
    def init(cls):
        if not cls.config:
            cls.config = json.load(cls.config_path.open())

    @classmethod
    def get_modak_endpoint(cls):
        cls.init()
        return os.getenv("MODAK_ENDPOINT", cls.config.get("MODAK_ENDPOINT", "localhost"))

    @classmethod
    def get_modak_api_image(cls):
        cls.init()
        api_image = os.getenv("MODAK_API_IMAGE", cls.config.get("MODAK_API_IMAGE", "/get_image"))
        return cls.get_modak_endpoint() + api_image

    @classmethod
    def get_modak_api_job(cls):
        cls.init()
        api_image = os.getenv("MODAK_API_JOB", cls.config.get("MODAK_API_JOB", "/get_job_content"))
        return cls.get_modak_endpoint() + api_image

    @classmethod
    def is_valid_image_property(cls, property):
        return property in cls.valid_container_image_properties

    @classmethod
    def get_opt_image(cls, opt_json_string: str):
        opt_json_string = opt_json_string.strip('\"')
        opt = json.loads(opt_json_string)
        response = requests.post(
            cls.get_modak_api_image(),
            headers= { "Content-Type": "application/json" },
            json= { "job": { "optimisation": opt.get("optimization", {}) } })
        if response.status_code != 200:
            print("Optimisation request error")
            return ""
        data = response.json()
        return data.get("job", {}).get("container_runtime", "")

    @classmethod
    def get_opt_job_content(cls, app, target, job_options, opt_json_string):
        opt_json_string = opt_json_string.strip('\"')
        opt = json.loads(opt_json_string) if opt_json_string else {}
        response = requests.post(
            cls.get_modak_api_job(),
            headers= { "Content-Type": "application/json" },
            json= { 
                "job": { 
                    "application": app,
                    "target": target,
                    "job_options": job_options,
                    "optimisation": opt.get("optimization", {}) 
                } 
            })
        if response.status_code != 200:
            print("Optimisation request error")
            return ""
        data = response.json()
        return data.get("job", {}).get("job_content", "")


class Context:
    def __init__(self, section, level):
        self.section = section
        self.level = level

    def add_level(self):
        return Context(self.section, self.level + 1)


class AadmPreprocessor:
    # regex to check if string is URL
    url_regex = r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&=\/]*)"
    # list of keys to convert
    convert_list_dict = ["properties", "attributes", "interfaces", "capabilities", "inputs"]
    convert_dict_list = ["constraints"]

    #path and urls
    ansible_urls = []
    ansible_paths = []
    dependency_urls = []
    dependency_paths = []

    # data in AADM JSON nodes is presented as lists
    # some lists must be converted to maps (dictionaries)
    # in order to be TOSCA complaint
    @classmethod
    def convert_list(cls, key, data):
        if isinstance(data, list) and key in cls.convert_list_dict:
            result = {}
            for item in data:
                if isinstance(item, dict):
                    for key_int, value in item.items():
                        result[key_int] = value
            return True, key, result
        return False, key, data

    # some maps must be converted to lists
    # in order to be TOSCA complaint
    @classmethod
    def convert_dict(cls, key, data):
        if isinstance(data, dict) and key in cls.convert_dict_list:
            result = []
            for key_int, value in data.items():                
                result.append({key_int : value})                    
            return True, key, result
        return False, key, data        

    #to convert get_input string to dict
    @classmethod
    def convert_str(cls, key, data):
        if isinstance(data, str) and "get_input" in data:
            get_str = data.strip("{ , }").split(":")
            if len(get_str) == 2:
                str_dict = '{{ "{}" : "{}"}}'.format(get_str[0],get_str[1].strip(" "))
                result = json.loads(str_dict)
                del data
                return True, key, result
        return False, key, data

    @classmethod
    def collapse_labels(cls, key, data):
        label = AadmPreprocessor.get_url(key)
        if (isinstance(data, dict)
                and "label" in data
                and data["label"] == label):
            del data["label"]
            return True, label, data
        return False, key, data

    # replace value maps with values
    @staticmethod
    def collapse_values(key, data):
        if (isinstance(data, dict)
                and "value" in data
                and len(data) == 1): 
            return True, key, data["value"]
        return False, key, data

    # in node type definitions specifications
    # should be just replaced with its content map
    @staticmethod
    def collapse_specifications(key, data):
        if (isinstance(data, dict)
                and "specification" in data
                and isinstance(data["specification"], dict)):
            spec = data["specification"]
            del data["specification"]
            data.update(spec)
            return True, key, data
        return False, key, data
    
    #formatting dependencies path and url
    @classmethod
    def dep_path_url(cls, key, data):
        if (isinstance(data, dict)
                and "files" in data):
            dep_path= []
            for ele in data["files"]:
                if("relative_path" in data):
                    path = '{}/{}'.format(data["relative_path"],cls.get_url(ele["path"]))
                else:
                    path_list = cls.get_path(ele["path"])
                    path = '{}/{}'.format(path_list[0],path_list[1])
                dep_path.append(path)
                if path not in cls.dependency_paths:
                    cls.dependency_urls.append(ele["url"])
                    cls.dependency_paths.append(path)
            return True, key, dep_path
        return False, key, data

    #formatting primary path and url
    @classmethod
    def pri_path_url(cls, key, data):
        if (isinstance(data, dict)
                and "primary" in data
                and isinstance(data["primary"], dict)):
            path = cls.get_path(data["primary"]["path"])
            uri = cls.get_url(data["primary"]["url"])
            cls.ansible_urls.append(data["primary"]["url"])
            data["primary"] = '{}/{}_{}'.format(path[0],uri,path[1])
            cls.ansible_paths.append(data["primary"])
            return True, key, data
        return False, key, data 

    #remove replace empty dictionaries with key values
    @staticmethod
    def collapse_empty_dict(key, data):
        if (isinstance(data, dict)
                and len(data) == 1):
            check = next(iter(data))
            if isinstance(data[check], dict) and len(data[check]) == 0:
                return True, key, check
        return False, key, data  

    # extract type values from URLs
    @classmethod
    def reduce_type(cls, key, data):
        short_type = cls.get_url(key)
        if short_type != key:
            return True, short_type, data
        return False, key, data

    #extract type out of URL
    @classmethod
    def get_url(cls, type_str):
        if re.search(cls.url_regex, type_str) is None:
            return type_str
        return type_str.split("/")[-1]

    #extract path out of url
    @classmethod
    def get_path(cls, path_str):
        if re.search(cls.url_regex, path_str) is None:
            return path_str
        return path_str.split('/')[-2:]

    #convert occurrences type from str to int in yaml.scalarnode
    @classmethod
    def convert_int(cls, tag):
        split_tag = tag.split(":") 
        get_url = split_tag[-1]
        if get_url=="str":
            base_tag = ":".join(split_tag[:2])
            ntag = base_tag + ":int"
        return ntag

    #recursively traverse the tree sequentially applying preprocessing rules
    @classmethod
    def preprocess_data(cls, key, data):
        preprocess_list = [
            cls.preprocess_data,
            cls.convert_list,
            cls.convert_dict,
            cls.collapse_labels,
            cls.collapse_values,
            cls.collapse_specifications,
            cls.collapse_empty_dict,
            cls.reduce_type,
            cls.dep_path_url,
            cls.pri_path_url,
            cls.convert_str
            ]

        changed = False
        result = data
        if isinstance(data, list):
            result = []
            for item in data:
                new_changed, new_key, new_value = cls.preprocess_data(None, item)
                changed = changed or new_changed
                result.append(new_value)
        if isinstance(data, dict):
            result = {}
            for key_int, value in data.items():
                result[key_int] = value
                for step in preprocess_list:
                    new_changed, new_key, new_value = step(key_int, value)
                    changed = changed or new_changed
                    if new_changed:
                        del result[key_int]
                        result[new_key] = new_value
                        break
        return changed, key, result

    @classmethod
    def preprocess_aadm(cls, aadm):
        cls.ansible_urls = []
        cls.ansible_paths = []
        cls.dependency_urls = []
        cls.dependency_paths = []
        result = {}  
        changed = True
        result = aadm.copy()
        while changed:
            # preprocess multiple times until no changes are applied to data
            changed = False
            for key, value in result.items():
                new_changed, new_key, new_value = cls.preprocess_data(key, value)
                changed = changed or new_changed
                result[new_key] = new_value
        return result


class AadmTransformer:

    # list of keys to remove from AADM
    skip_list = ["isNodeTemplate", "class"]

    # valid tosca types
    valid_tosca_types = [
        "artifact_types", "capability_types" , "data_types", "group_types", 
        "interface_types", "node_types", "policy_types", "relationship_types",
    ]
    
    #set types
    @staticmethod
    def transform_type(data, context):
        prefix = "type" if context.section == "node_templates" or context.level != 0 else "derived_from"
        if isinstance(data, str):
            return prefix, AadmPreprocessor.get_url(data)
        raise Exception

    @staticmethod
    def transform_function_parametres(data, context):
        if isinstance(data, dict):
            result = []
            if "entity" in data:
                result.append(data["entity"])
            if "req_cap" in data:
                if isinstance(data["req_cap"], list):
                    result.append(data["req_cap"][0])
                else:    
                    result.append(data["req_cap"])
            if "property" in data:
                result.append(data["property"])
            if "attribute" in data:
                result.append(data["attribute"])
            return result
        return data

    @classmethod
    def transform(cls, data, context):
        transform_map = {
            "type": cls.transform_type,
            "get_property": cls.transform_function_parametres,
            "get_attribute": cls.transform_function_parametres,
            }

        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key in cls.skip_list:
                    transformation = None
                elif key in transform_map:
                    transformation = transform_map[key](value, context)
                elif isinstance(value, dict):
                    transformation = cls.transform(value, context.add_level())
                else:
                    transformation = (key, value)

                if isinstance(transformation, tuple):
                    result[transformation[0]] = transformation[1]
                elif transformation is not None:
                    result[key] = transformation   

            return result
        return data

    @classmethod
    def transform_optimization(cls, result):
        opt_nodes = {}
        exec_nodes = {}

        # extract optimization from nodes and assign empty to non-optimized
        for key, value in result["node_templates"].items():
            opt_nodes[key] = value.get("optimization", "")
            value.pop("optimization", None)

        # extract execution nodes
        for key, value in result["node_templates"].items():
            reqs = value.get("requirements", [])
            
            # determine an execution node from the list of requirements
            reqs_names = [
                req_name
                for req in reqs 
                for req_name in req.keys()
            ]
            if not all(exec_req in reqs_names for exec_req in ModakConfig.exec_node_requirements):
                continue
            
            for req in reqs:
                app_req = req.get("application", "")
                if isinstance(app_req, dict):
                    app_req = app_req.get("node", "")

                if app_req in opt_nodes:
                    exec_nodes[key] = app_req

        # modify image properties for optimization nodes
        for node, opts in opt_nodes.items():
            if not opts:
                continue

            for property in result["node_templates"][node]["properties"]:
                if ModakConfig.is_valid_image_property(property):
                    opt_image = ModakConfig.get_opt_image(opts)
                    if opt_image:
                        result["node_templates"][node]["properties"][property] = opt_image

        # modify content properties for execution nodes
        for node, opt_node in exec_nodes.items():
            host_node = {}
            for req in result["node_templates"][node].get("requirements", []):
                host_req = req.get("host", "")
                if isinstance(host_req, dict):
                    host_req = host_req.get("node", "")
                if host_req:
                    host_node = result["node_templates"][host_req]

            content = ModakConfig.get_opt_job_content(
                app = result["node_templates"][opt_node]["properties"],
                target = cls.resolve_optimization_target(host_node),
                job_options = result["node_templates"][node]["properties"],
                opt_json_string = opt_nodes[opt_node],
            )
            result["node_templates"][node]["properties"]["content"] = content

    @classmethod
    def resolve_optimization_target(cls, node):
        target = {}
        scheduler = node.get("properties", {}).get("scheduler")
        if scheduler:
            target["job_scheduler_type"] = scheduler
        opt_caps = node.get("capabilities", {}).get("optimisations", {})
        name = opt_caps.get("properties", {}).get("target")
        if name:
            target["name"] = name
        return target

    @classmethod
    def transform_aadm(cls, aadm):
        result = {
             "tosca_definitions_version": "tosca_simple_yaml_1_3",
             "node_types": {},
             "node_templates": {},
             "input": {}
             }
        top_key = None
        for key, value in aadm.items():
            
            if "topology_template_inputs" in key:                
                section = "input"
                value = value["inputs"]
                top_key = AadmPreprocessor.get_url(key)

            elif "isNodeTemplate" in value:
                if value["isNodeTemplate"]:
                    section = "node_templates"
                else:
                    tosca_type_class = value.get("class", "")
                    if tosca_type_class in cls.valid_tosca_types:
                        if tosca_type_class not in result:
                            result[tosca_type_class] = {}
                        section = tosca_type_class
                    else:
                        continue
            else:
                continue

            context = Context(section, 0)
            key = cls.transform_type(key, context)[1]
            result[section][key] = cls.transform(value, context)

        cls.transform_optimization(result)

        result["topology_template"] = {}
        if top_key:
            result["topology_template"]["inputs"] = result["input"][top_key]
        result["topology_template"]["node_templates"] = result["node_templates"]        
        del result["node_templates"]
        del result["input"]
        return result

class ToscaDumper(yaml.SafeDumper):
    def __init__(self, stream,
                 default_style=None, default_flow_style=False,
                 canonical=None, indent=None, width=None,
                 allow_unicode=None, line_break=None,
                 encoding=None, explicit_start=None, explicit_end=None,
                 version=None, tags=None, sort_keys=False):
        super().__init__(stream, default_flow_style=False, sort_keys=False)
        self.line_break_indent = 2

    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) <= self.line_break_indent:
            super().write_line_break()

    def serialize_node(self, node, parent, index, flow_style=False):
        if isinstance(index, ScalarNode) and index.value == "node_templates":
            self.line_break_indent = 3

        # output inputs in json-like format
        if isinstance(index, ScalarNode) and index.value == "inputs":
            for key, value in node.value:
                if isinstance(value, CollectionNode):
                    value.flow_style = True

        # output inputs in json-like format
        if (isinstance(index, ScalarNode)
                and index.value in ["properties", "attributes"]):
            for key, value in node.value:
                if (isinstance(value, MappingNode)
                        and ("get_input" in str(value.value)
                             or "get_attribute" in str(value.value)
                             or "get_property" in str(value.value))):
                    value.flow_style = True    
        if (isinstance(node, SequenceNode)
                and isinstance(index, ScalarNode)
                and index.value == "occurrences"):
            node.flow_style = True
            for ele in node.value:
                if isinstance(ele, ScalarNode) and ele.value.isdigit():
                    ele.tag = AadmPreprocessor.convert_int(ele.tag)

        super().serialize_node(node, parent, index)

def parse_data(name, data):
    preprocessed_aadm = AadmPreprocessor.preprocess_aadm(data)
    tosca = AadmTransformer.transform_aadm(preprocessed_aadm)

    # create an output file
    with open(name + ".yml", 'w+') as outfile:
        print('TOSCA generated -------')
        yaml.dump(tosca, outfile, Dumper=ToscaDumper)        

    return (AadmPreprocessor.ansible_urls, AadmPreprocessor.ansible_paths, AadmPreprocessor.dependency_urls, AadmPreprocessor.dependency_paths)

'''
#UNRELATED AUX FUNC
def read(path):
    return (pathlib.Path(path)).read_text()

def main():
    json_aadm = json.loads(read("test/fixture.json"))
    parse_data("test/outputs/fixt", json_aadm)  

if __name__ == "__main__":
    main()

'''    