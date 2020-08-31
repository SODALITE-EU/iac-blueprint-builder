# import unittest
# target = __import__("src")
import json
from src import parse


def test_parser():
    # expected ansible_files, expected ansible_paths, expected dependency_files, expected dependency_paths
    expected = (['http://160.40.52.200:8084/Ansibles/97d6afb6-7ed5-4400-af71-f1e6afc9bef5',
                 'http://160.40.52.200:8084/Ansibles/8472698e-044e-470b-9805-7bc5046f3146',
                 'http://160.40.52.200:8084/Ansibles/e0a2fe8a-b902-4a05-ab00-8638b4308705',
                 'http://160.40.52.200:8084/Ansibles/ffdf5083-a0b3-48e4-9891-8237d259e4e3',
                 'http://160.40.52.200:8084/Ansibles/4728fc1a-6c69-483e-a85c-a768ef7b5c4f',
                 'http://160.40.52.200:8084/Ansibles/1ef463c3-ea3e-4e2d-9ed0-f0e9c3d2bf4f',
                 'http://160.40.52.200:8084/Ansibles/76d494af-219b-492e-b263-886a42414399',
                 'http://160.40.52.200:8084/Ansibles/b9a151d2-e838-4ff4-94b8-1083e2984d7a',
                 'http://160.40.52.200:8084/Ansibles/35d91cc4-f4f0-44f2-af2d-080607a18456',
                 'http://160.40.52.200:8084/Ansibles/013923c7-4f85-42f9-9a7a-800a5c9af1dd',
                 'http://160.40.52.200:8084/Ansibles/9c0a5a59-ea21-4674-b29a-cccb3eb8c2a5',
                 'http://160.40.52.200:8084/Ansibles/d0ee2abc-ec33-43f8-bf43-7164753394e0',
                 'http://160.40.52.200:8084/Ansibles/3749fe0a-c9c3-4107-9eee-6f0fd75a4dcf',
                 'http://160.40.52.200:8084/Ansibles/b1953769-a682-4acc-93f0-a1cd6e92dded',
                 'http://160.40.52.200:8084/Ansibles/afcc8b50-3807-49ab-97f4-e2b38a966acb',
                 'http://160.40.52.200:8084/Ansibles/9cb93c9d-aa87-4188-8b72-14934b25bee8',
                 'http://160.40.52.200:8084/Ansibles/5a924a8d-16a1-4263-b620-5334a2c10514'],

                ['playbooks/97d6afb6-7ed5-4400-af71-f1e6afc9bef5_add_volume.yml',
                 'playbooks/8472698e-044e-470b-9805-7bc5046f3146_remove_volume.yml',
                 'playbooks/e0a2fe8a-b902-4a05-ab00-8638b4308705_add_container.yml',
                 'playbooks/ffdf5083-a0b3-48e4-9891-8237d259e4e3_remove_container.yml',
                 'playbooks/4728fc1a-6c69-483e-a85c-a768ef7b5c4f_create_docker_host.yml',
                 'playbooks/1ef463c3-ea3e-4e2d-9ed0-f0e9c3d2bf4f_delete_docker_host.yml',
                 'playbooks/76d494af-219b-492e-b263-886a42414399_vm_create.yml',
                 'playbooks/b9a151d2-e838-4ff4-94b8-1083e2984d7a_vm_delete.yml',
                 'playbooks/35d91cc4-f4f0-44f2-af2d-080607a18456_login_user.yml',
                 'playbooks/013923c7-4f85-42f9-9a7a-800a5c9af1dd_logout_user.yml',
                 'playbooks/9c0a5a59-ea21-4674-b29a-cccb3eb8c2a5_security_rule_create.yml',
                 'playbooks/d0ee2abc-ec33-43f8-bf43-7164753394e0_security_rule_delete.yml',
                 'playbooks/3749fe0a-c9c3-4107-9eee-6f0fd75a4dcf_add_cert.yml',
                 'playbooks/b1953769-a682-4acc-93f0-a1cd6e92dded_remove_cert.yml',
                 'playbooks/afcc8b50-3807-49ab-97f4-e2b38a966acb_configure_demo.yml',
                 'playbooks/9cb93c9d-aa87-4188-8b72-14934b25bee8_add_network.yml',
                 'playbooks/5a924a8d-16a1-4263-b620-5334a2c10514_remove_network.yml'],

                ['http://160.40.52.200:8084/Ansibles/ecc0d4dd-f559-4ce7-b0eb-c72992362326',
                 'http://160.40.52.200:8084/Ansibles/8960e765-1f31-4bf2-a3cf-aadf7a96c5af',
                 'http://160.40.52.200:8084/Ansibles/f8b77694-50d3-4491-ad2c-570d66936562',
                 'http://160.40.52.200:8084/Ansibles/9082492d-a625-4ce7-8b12-9388db367d3a',
                 'http://160.40.52.200:8084/Ansibles/76c43a80-16a4-48bf-b08e-036dc72a864b',
                 'http://160.40.52.200:8084/Ansibles/8499031d-0281-414f-b608-938833f4f0d1',
                 'http://160.40.52.200:8084/Ansibles/b8ddac49-6c25-4815-b6e1-2029590f1fd6'],

                ['artifacts/egi_refresh_token.yml',
                 'artifacts/egi_refresh_token.yml',
                 'artifacts/egi_refresh_token.yml',
                 'artifacts/egi_refresh_token.yml',
                 'artifacts/ca.key',
                 'artifacts/ca.crt',
                 'artifacts/config.json.tmpl'])

    with open('test/fixture.json') as f:
        t = json.load(f)
        parsed_data = parse(t)
        pds = []
        exs = []
        for i in range(0, 3):
            pds.append(set(parsed_data[i]))
            exs.append(set(expected[i]))
        assert exs == pds
