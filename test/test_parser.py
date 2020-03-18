# import unittest
# target = __import__("src")
import pytest
import json
from src import parse
#

def test_parser():
    expected = [
        'http://160.40.52.200:8084/Ansibles/playbooks/docker/dockerized_component_undeploy.yml',
        'http://160.40.52.200:8084/Ansibles/playbooks/docker/dockerized_component_deploy.yml', 
        'http://160.40.52.200:8084/Ansibles/playbooks/openstack/vm/delete.yml', 
        'http://160.40.52.200:8084/Ansibles/playbooks/openstack/vm/create.yml', 
        'http://160.40.52.200:8084/Ansibles/playbooks/openstack/security-rule/create.yml', 
        'http://160.40.52.200:8084/Ansibles/playbooks/openstack/security-rule/delete.yml', 
        'http://160.40.52.200:8084/Ansibles/playbooks/docker/destroy_docker_host.yml', 
        'http://160.40.52.200:8084/Ansibles/playbooks/docker/create_docker_host.yml']
    
    with open('test/fixture.json') as f:
        t = json.load(f)
        assert parse(t["data"]) == expected



