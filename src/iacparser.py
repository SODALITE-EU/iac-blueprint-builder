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
    convert_list_dict = ["properties", "attributes", "interfaces", "capabilities"]

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

    #to convert get_input string to dict
    @classmethod
    def convert_str(cls, key, data):
        if isinstance(data, str) and "get_input" in data:
            get_str = data.strip("{ , }").split(":")
            str_dict = '{{ "{}" : "{}"}}'.format(get_str[0],get_str[1].strip(" "))
            result = json.loads(str_dict)
            del data
            return True, key, result
        return False, key, data

    @classmethod
    def collapse_labels(cls, key, data):
        label = AadmPreprocessor.get_type(key)
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
    
    #convert "files" from list to dict 
    #to configure path and url
    @staticmethod
    def file_list_dict(key, data):
        if (isinstance(data, dict)
                and "files" in data
                and isinstance(data["files"], list)):
            list_dict = data["files"][0]
            data["files"] = list_dict
            return True, key, data
        return False, key, data

    #formatting path and url to download playbooks
    @staticmethod
    def format_path_url(key,data):
        if (isinstance(data, dict)
                and "path" in data):
            path = AadmPreprocessor.get_path(data["path"])
            uri = AadmPreprocessor.get_type(data["url"])
            pth = '{}/{}_{}'.format(path[0],uri,path[1])
            del data["path"]
            del data["url"]
            return True, key, pth
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
        short_type = cls.get_type(key)
        if short_type != key:
            return True, short_type, data
        return False, key, data

    #extract type out of URL
    @classmethod
    def get_type(cls, type_str):
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
        get_type = split_tag[-1]
        if get_type=="str":
            base_tag = ":".join(split_tag[:2])
            ntag = base_tag + ":int"
        return ntag

    #recursively traverse the tree sequentially applying preprocessing rules
    @classmethod
    def preprocess_data(cls, key, data):
        preprocess_list = [
            cls.preprocess_data,
            cls.convert_list,
            cls.collapse_labels,
            cls.collapse_values,
            cls.collapse_specifications,
            cls.collapse_empty_dict,
            cls.reduce_type,
            cls.file_list_dict,
            cls.format_path_url,
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
    skip_list = ["isNodeTemplate"]

    #optimization parameters
    valid_container_image_properties = ["image", "image_name"]
    
    #set types
    @staticmethod
    def transform_type(data, context):
        prefix = "type" if context.section == "node_templates" or context.level != 0 else "derived_from"
        if isinstance(data, str):
            return prefix, AadmPreprocessor.get_type(data)
        raise Exception

    @staticmethod
    def transform_function_parametres(data, context):
        if isinstance(data, dict):
            result = []
            if "entity" in data:
                result.append(data["entity"])
            if "req_cap" in data:
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
    def get_opt_image(cls, opt_json_string: str):
        opt_json_string = opt_json_string.strip('\"')
        opt = json.loads(opt_json_string)
        response = requests.post(
            ModakConfig.get_modak_api_image(),
            headers= { "Content-Type": "application/json" },
            json= { "job": { "optimisation": opt.get("optimization", {}) } })
        if response.status_code != 200:
            print("Optimisation request error")
            return ""
        data = response.json()
        image = data.get("job", {}).get("container_runtime", "").split("://", 1)
        return image[1] if len(image) > 1 else image[0]

    @classmethod
    def transform_optimization(cls, value):
        if "optimization" in value:
            opt_json_str = value['optimization']
            del value["optimization"]
            if opt_json_str:
                for property in value["properties"]:
                    if property in cls.valid_container_image_properties:
                        opt_image = cls.get_opt_image(opt_json_str)
                        if opt_image:
                            value["properties"][property] = opt_image

    @classmethod
    def transform_aadm(cls, aadm):
        result = {
             "tosca_definitions_version": "tosca_simple_yaml_1_3",
             "node_types": {},
             "node_templates": {}
             }

        for key, value in aadm.items():
            if "isNodeTemplate" not in value:
                continue

            if value["isNodeTemplate"]:
                section = "node_templates"
            else:
                if "sodalite.datatypes" in key:
                    if "data_types" not in result:
                        result["data_types"] = {}
                    section = "data_types"

                elif "sodalite.relationships" in key:
                    if "relationship_types" not in result:
                        result["relationship_types"] = {}
                    section = "relationship_types"
                else:
                    section = "node_types"

            cls.transform_optimization(value)

            context = Context(section, 0)
            key = cls.transform_type(key, context)[1]
            result[section][key] = cls.transform(value, context)

        result["topology_template"] = {}
        result["topology_template"]["node_templates"] = result["node_templates"]
        del result["node_templates"]
        return result


class ToscaDumper(yaml.SafeDumper):
    def __init__(self, stream,
                 default_style=None, default_flow_style=False,
                 canonical=None, indent=None, width=None,
                 allow_unicode=None, line_break=None,
                 encoding=None, explicit_start=None, explicit_end=None,
                 version=None, tags=None, sort_keys=False):
        super().__init__(stream, default_flow_style=False, sort_keys=False)

    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) <= 2:
            super().write_line_break()

    def serialize_node(self, node, parent, index, flow_style=False):

        # output inputs in json-like format
        if isinstance(index, ScalarNode) and index.value == "inputs":
            for key, value in node.value:
                if isinstance(value, CollectionNode):
                    value.flow_style = True
        
        # output inputs in json-like format
        if (isinstance(index, ScalarNode)
                and index.value == "properties"):
            for key, value in node.value:
                if (isinstance(value, MappingNode)
                        and "get_input" in str(value.value)):
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
        return yaml.dump(tosca, outfile, Dumper=ToscaDumper)        

    return None #ansible_urls, ansible_paths, dependency_urls, dependency_paths    

#UNRELATED AUX FUNC
def read(path):
    return (pathlib.Path(path)).read_text()

def main():
    json_aadm = json.loads(read("test/fixture.json"))
    parse_data("test/fixture", json_aadm)  

if __name__ == "__main__":
    main()  