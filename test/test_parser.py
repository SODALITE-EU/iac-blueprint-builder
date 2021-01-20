import json
import yaml
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

    test = TestConfig("fixture")
    parsed_data = parser.parse_data(test.parser_dest(), test.fixture())

    pds = []
    exs = []
    for i in range(0, 3):
        pds.append(set(parsed_data[i]))
        exs.append(set(expected[i]))
    assert exs == pds
        

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

    assert image_name == opt_expected_container_runtime

    opt_not_found_component_template = service.get("topology_template").get("node_templates").get(opt_not_found_component)
    image_name = opt_not_found_component_template.get("properties").get("image_name")

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

    assert image == opt_expected_container_runtime

    job_script_component_template = service.get("topology_template").get("node_templates").get(job_script_component)
    content = job_script_component_template.get("properties").get("content", "")

    assert len(content) > 0

    assert "#PBS -N skyline-extraction-training" in content
    assert "#PBS -q ssd" in content
    assert "#PBS -l nodes=1:gpus=1:ssd" in content
    assert "#PBS -l procs=40" in content
