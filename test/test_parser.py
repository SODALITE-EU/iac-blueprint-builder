import json
import yaml
import re
import pytest
from pathlib import Path

import src.iacparser as parser


class TestConfig:

    YAML_SUFFIX = ".yml"
    OUTPUTS = Path("test/outputs")
    FIXTURE = "test/fixture.json"

    def __init__(self, test_name, fixture_json=None):
        self.test_path = self.OUTPUTS / test_name
        self.fixture_path = Path(fixture_json) if fixture_json else Path(self.FIXTURE)

    def fixture(self):
        return json.load(self.fixture_path.open())

    def parser_dest(self):
        return str(self.test_path)

    def yaml_path(self):
        return self.test_path.with_suffix(self.YAML_SUFFIX)

    def service(self):
        return yaml.load(self.yaml_path().open())

#return a new class TestConfig
@pytest.fixture
def test_fixture():
    test = TestConfig('output_test')
    parser.parse_data(test.parser_dest(), test.fixture())
    return test

#return loaded json
@pytest.fixture
def json_in(test_fixture):
    return test_fixture.fixture()

#return loaded yaml
@pytest.fixture
def yaml_out(test_fixture):
    return test_fixture.service()


def test_artifacts_extraction():
    # expected ansible_files, expected ansible_paths, expected dependency_files, expected dependency_paths
    expected = (['http://160.40.52.200:8084/Ansibles/ddce9b4f-7eef-46b9-b3d6-80f58eb5bb84', 
                'http://160.40.52.200:8084/Ansibles/3b95de8b-4815-4f00-9ee4-cedf49df4afb', 
                'http://160.40.52.200:8084/Ansibles/b8812f8a-7e1d-4acb-9258-45a5bdb45af2', 
                'http://160.40.52.200:8084/Ansibles/454ab4e5-43f2-479a-b31a-619596e0a696', 
                'http://160.40.52.200:8084/Ansibles/0ed0c21b-5614-48cf-82bc-cf7db4369f5b', 
                'http://160.40.52.200:8084/Ansibles/85767023-d35f-49bc-90c0-e79fe21351eb', 
                'http://160.40.52.200:8084/Ansibles/2a1e0e73-bcb8-4e6c-9c0d-0580cc5495b5', 
                'http://160.40.52.200:8084/Ansibles/85578876-343f-4e5b-ba1e-b1abfab8f6d3', 
                'http://160.40.52.200:8084/Ansibles/4250caa5-0a7d-42c1-98ae-92bb3d0dc82f', 
                'http://160.40.52.200:8084/Ansibles/7d35630c-fd17-45d6-9ccd-3c373ee0ee91', 
                'http://160.40.52.200:8084/Ansibles/15dbb35b-d70f-4458-a7c2-47fd39240fee', 
                'http://160.40.52.200:8084/Ansibles/d1e603eb-1261-4d73-90b9-683d3fd7d301', 
                'http://160.40.52.200:8084/Ansibles/67830dce-dabd-447f-81ab-9d2b57615331', 
                'http://160.40.52.200:8084/Ansibles/55f5be63-2220-4e62-9b6d-c15b69f82e9e', 
                'http://160.40.52.200:8084/Ansibles/88943b50-fdd9-4d5e-b72a-5fca96baaf27', 
                'http://160.40.52.200:8084/Ansibles/31f26aa0-cb6a-446c-b6c2-9c5e846b10e4', 
                'http://160.40.52.200:8084/Ansibles/0fc36efb-5153-49d5-9074-ed7fc66b88a4'],

                ['playbooks/ddce9b4f-7eef-46b9-b3d6-80f58eb5bb84_remove_network.yml', 
                'playbooks/3b95de8b-4815-4f00-9ee4-cedf49df4afb_add_network.yml', 
                'playbooks/b8812f8a-7e1d-4acb-9258-45a5bdb45af2_remove_container.yml', 
                'playbooks/454ab4e5-43f2-479a-b31a-619596e0a696_add_container.yml', 
                'playbooks/0ed0c21b-5614-48cf-82bc-cf7db4369f5b_remove_cert.yml', 
                'playbooks/85767023-d35f-49bc-90c0-e79fe21351eb_remove_volume.yml', 
                'playbooks/2a1e0e73-bcb8-4e6c-9c0d-0580cc5495b5_add_volume.yml', 
                'playbooks/85578876-343f-4e5b-ba1e-b1abfab8f6d3_create_docker_host.yml', 
                'playbooks/4250caa5-0a7d-42c1-98ae-92bb3d0dc82f_delete_docker_host.yml', 
                'playbooks/7d35630c-fd17-45d6-9ccd-3c373ee0ee91_login_user.yml', 
                'playbooks/15dbb35b-d70f-4458-a7c2-47fd39240fee_logout_user.yml', 
                'playbooks/d1e603eb-1261-4d73-90b9-683d3fd7d301_add_cert.yml', 
                'playbooks/67830dce-dabd-447f-81ab-9d2b57615331_security_rule_delete.yml', 
                'playbooks/55f5be63-2220-4e62-9b6d-c15b69f82e9e_security_rule_create.yml', 
                'playbooks/88943b50-fdd9-4d5e-b72a-5fca96baaf27_vm_create.yml', 
                'playbooks/31f26aa0-cb6a-446c-b6c2-9c5e846b10e4_vm_delete.yml', 
                'playbooks/0fc36efb-5153-49d5-9074-ed7fc66b88a4_configure_demo.yml'],

                ['http://160.40.52.200:8084/Ansibles/fde69a72-7375-4fef-adc7-e941cb985eec', 
                'http://160.40.52.200:8084/Ansibles/d6f34eaa-25cf-40fb-a31a-da244c0c9d37', 
                'http://160.40.52.200:8084/Ansibles/b8ad4903-01db-4433-8eaa-cbff67edee9b', 
                'http://160.40.52.200:8084/Ansibles/4ba88e9d-2f5a-43b7-b658-3ff59fe5c3cc', 
                'http://160.40.52.200:8084/Ansibles/c91b757e-2cb5-4596-b80f-bdbea6fb4ccd', 
                'http://160.40.52.200:8084/Ansibles/30c3abbe-7718-433e-bf3b-dab3093d690d', 
                'http://160.40.52.200:8084/Ansibles/2dd0cacf-014c-4c08-a211-d222e41d3c21'],

                ['artifacts/ca.key',
                 'artifacts/ca.crt',
                 'playbooks/egi_refresh_token.yml',
                 'playbooks/config.json.tmpl'])

    test = TestConfig("fixture", "test/fixture.json")

    parsed_data = parser.parse_data(test.parser_dest(), test.fixture())
    pds = []
    exs = []
    for i in range(0, 3):
        pds.append(parsed_data[i])
        exs.append(expected[i])
    assert exs == pds

    # check values reset
    parsed_data = parser.parse_data(test.parser_dest(), test.fixture())
    pds = []
    exs = []
    for i in range(0, 3):
        pds.append(parsed_data[i])
        exs.append(expected[i])
    assert exs == pds

#checking if the output file is sucssesful generated
def test_output_path(test_fixture):
    assert Path.exists(test_fixture.yaml_path()),"output yaml not found"

#checking if all participants are listed in the output
def test_node_template_participants(json_in, yaml_out):
    node_temp = list(yaml_out.get("topology_template").get("node_templates").keys())
    for temp in next(iter(json_in.values()))["participants"]:
        temp = str(temp)[str(temp).rfind('/') + 1:]
        if "topology_template_inputs" not in temp:
            assert temp in node_temp,"Participant missing"

#checking if all the node types are generated
def test_node_types_list(json_in, yaml_out):
    node_type = list(yaml_out.get("node_types").keys())
    for key in list(json_in.keys()):
        key = str(key)[str(key).rfind('/') + 1:]
        if key.find('sodalite.nodes.') == 0:
            assert key in node_type

#checking the detail information in node_templates for fields: 
#   type, properties, requirement
def test_node_template_details(json_in,yaml_out):
    node_temp = yaml_out.get("topology_template").get("node_templates")
    node_list = list(node_temp.keys())
    for key, value in json_in.items():
        key = str(key)[str(key).rfind('/') + 1:]
        if key in node_list:
            node_out = node_temp.get(key)
            if "type" in value.keys():
                t = value["type"]
                assert remove_link(t) == node_out.get("type"), "type is not correct"
            if "properties" in value.keys():
                for pro_item in value["properties"]:
                    for key_pro, value_pro in pro_item.items():
                        if isinstance(value_pro, dict) and "value" in value_pro.keys() and "label" in value_pro.keys():
                            node_pro = node_out.get("properties").get(value_pro["label"])
                            if isinstance(node_pro, dict):
                                key_v = re.search('{\s(.+?):', value_pro["value"]).group(1)
                                value_v = re.search(':\s(.+?)\s}', value_pro["value"]).group(1)
                                assert key_v in node_pro.keys() and value_v in node_pro.values(),"properties error with label and value"
                                pass #later
                            elif isinstance(node_pro, list):
                                for item in node_pro:
                                    assert item in value_pro["value"], "properties error with label and value"
                            else:
                                assert node_pro == value_pro["value"], "properties error with label and value"
            if "requirements" in value.keys():
                node_req = node_out.get("requirements")
                for req_index in range(0, len(value["requirements"])):
                    for key_req, value_req in value["requirements"][req_index].items():
                        if "value" in value_req.keys():
                            sub_value_req = value_req["value"]
                            for key_sub, value_sub in sub_value_req.items():
                                if "https://" in key_sub and (isinstance(value_sub, dict) and "label" in value_sub.keys()):
                                    assert node_req[req_index].get(sub_value_req["label"]) == value_sub["label"] ,"requirement error with label and value"

#checking topology template inputs
def test_topology_template_inputs(json_in,yaml_out):
    inputs_out = yaml_out.get("topology_template").get("inputs")
    inputs_in = []
    for key, value in json_in.items():
        if "topology_template_inputs" in key:
            inputs_in = value["inputs"]
    for element in inputs_in:
        for key, value in element.items():
            if "https://" in key: 
                key = remove_link(key)
                assert inputs_out.get(key).get("type") == value["specification"]["type"], "input type not correct"

#checking node types details for: 
#   type/derived_from, properties(description, required, type)
#   attributes(description, specification), requirements, capabilities
def test_node_types_detail(json_in, yaml_out):
    node_type = yaml_out.get("node_types")
    for key, value in json_in.items():
        key = remove_link(key)
        if key.find('sodalite.nodes.') == 0:
            node = node_type.get(key)
            #derived from:
            if "type" in value.keys() and "https://" in value["type"]: 
                type_in = remove_link(value["type"])
                assert node.get("derived_from") == type_in, "node type derived_from error"
            if "properties" in value.keys():
                node_pro = node.get("properties")
                for element in value["properties"]:
                    for key_pro, value_pro in element.items():
                        key_pro = remove_link(key_pro)
                        if "description" in value_pro.keys():
                            assert node_pro.get(key_pro).get("description") == value_pro["description"], "node type properties description error"
                        if "specification" in value_pro.keys():
                            value_spec = value_pro["specification"]
                            if "required" in value_spec.keys():
                                assert node_pro.get(key_pro).get("required") == value_spec["required"], "properties required error"
                            if "type" in value_spec.keys():
                                for key_type, value_type in value_spec["type"].items():
                                    assert node_pro.get(key_pro).get("type") == value_type["label"], "properties type error"
            if "attributes" in value.keys():
                node_att = node.get("attributes")
                for element in value["attributes"]:
                    for key_att, value_att in element.items():
                        key_att = remove_link(key_att)
                        if "description" in value_att.keys():
                            assert node_att.get(key_att).get("description") == value_att["description"], "node type attribute description error"
                        if "specification" in value_att.keys():
                            value_spec = value_att["specification"]
                            if "type" in value_spec.keys():
                                for key_type, value_type in value_spec["type"].items():
                                    assert node_att.get(key_att).get("type") == value_type["label"], "attribute type error"
            if "requirements" in value.keys():
                node_req = node.get("requirements")
                for req_index in range(0, len(value["requirements"])):
                    for key_req, value_req in value["requirements"][req_index].items():
                        key_req = remove_link(key_req)
                        if "specification" in value_req.keys():
                            for key_sp, value_sp in value_req["specification"].items():
                                if isinstance(value_sp, dict):
                                    for key_sub, value_sub in value_sp.items():
                                        if "label" in value_sub.keys():
                                            assert node_req[req_index].get(key_req).get(key_sp) == value_sub["label"], "node type requirement specification error"
                                if isinstance(value_sp, list):
                                    req_list = node_req[req_index].get(key_req).get(key_sp)
                                    for index in range(0, len(req_list)):
                                        assert str(req_list[index]) == value_sp[index], "node type requirement specification error"
            if "capabilities" in value.keys():
                node_cap = node.get("capabilities")
                for element in value["capabilities"]:
                    for key_cap, value_cap in element.items():
                        key_cap = remove_link(key_cap)
                        for key_label, value_label in value_cap["specification"]["type"].items():
                            assert node_cap.get(key_cap).get("type") == value_label["label"], "node type capability specification error"




                                    




#helper funciton to extract info from links
def remove_link(link):
    return link[link.rfind('/')+1:]        


def test_parser_opt():

    # this component has optimisation field
    opt_component = "optimization-skyline-extractor"
    # expected container for $opt_component
    opt_expected_container_runtime = "docker://modakopt/modak:tensorflow-2.1-gpu-src"

    # this component has optimisation field, but optimised container not found
    opt_not_found_component = "optimization-skyline-alignment"
    # expected container for $opt_not_found_component
    opt_not_found_expected_container_runtime = "snow-skyline-alignment:latest"


    test = TestConfig("opt", "test/opt_fixture.json")
    parser.parse_data(test.parser_dest(), test.fixture())
    service = test.service()

    opt_component_template = service.get("topology_template").get("node_templates").get(opt_component)
    image_name = opt_component_template.get("properties").get("image_name")

    assert not "optimization" in opt_component_template
    assert image_name == opt_expected_container_runtime

    opt_not_found_component_template = service.get("topology_template").get("node_templates").get(opt_not_found_component)
    image_name = opt_not_found_component_template.get("properties").get("image_name")

    assert not "optimization" in opt_not_found_component_template
    assert image_name == opt_not_found_expected_container_runtime

def test_parser_opt_job():

    # this component has optimisation field
    opt_component = "batch-app"
    # expected container for $opt_component
    opt_expected_container_runtime = "docker://modakopt/modak:tensorflow-2.1-gpu-src"

    # this component has optimisation field, but optimised container not found
    job_script_component = "batch-app-job-hpc"


    test = TestConfig("opt_job", "test/opt_job_fixture.json")
    parser.parse_data(test.parser_dest(), test.fixture())
    service = test.service()

    opt_component_template = service.get("topology_template").get("node_templates").get(opt_component)
    image = opt_component_template.get("properties").get("container_runtime")

    assert not "optimization" in opt_component_template
    assert image == opt_expected_container_runtime

    job_script_component_template = service.get("topology_template").get("node_templates").get(job_script_component)
    content = job_script_component_template.get("properties").get("content", "")

    assert len(content) > 0

    assert "#PBS -N skyline-extraction-training" in content
    assert "#PBS -q ssd" in content
    assert "#PBS -l nodes=1:gpus=1:ssd" in content
    assert "#PBS -l procs=40" in content

def test_parser_no_opt_job():

    # this component has optimisation field
    no_opt_component = "no-opt-batch-app"
    # expected container for $no_opt_component
    no_opt_expected_container_runtime = "docker://some-container"

    # this component has optimisation field, but optimised container not found
    job_script_component = "no-opt-batch-app-job-hpc"


    test = TestConfig("no_opt_job", "test/opt_job_fixture.json")
    parser.parse_data(test.parser_dest(), test.fixture())
    service = test.service()

    no_opt_component_template = service.get("topology_template").get("node_templates").get(no_opt_component)
    image = no_opt_component_template.get("properties").get("container_runtime")

    assert not "optimization" in no_opt_component_template
    assert image == no_opt_expected_container_runtime

    job_script_component_template = service.get("topology_template").get("node_templates").get(job_script_component)
    content = job_script_component_template.get("properties").get("content", "")

    assert len(content) > 0

    assert "#PBS -N no-opt-skyline-extraction-training" in content
    assert "#PBS -q ssd" in content
    assert "#PBS -l nodes=1:gpus=1:ssd" in content
    assert "#PBS -l procs=40" in content

