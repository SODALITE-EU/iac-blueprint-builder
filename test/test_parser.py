# import unittest
# target = __import__("src")
import json
from src import parse


def test_parser():
    # expected ansible_files, expected ansible_paths, expected dependency_files, expected dependency_paths
    expected = (['http://160.40.52.200:8084/Ansibles/2d57b396-0e23-479e-972e-49f1ee33417c',
                 'http://160.40.52.200:8084/Ansibles/e8f67cde-c4b5-4beb-94a8-5c08e94cac22',
                 'http://160.40.52.200:8084/Ansibles/3828dab9-220f-4f38-b425-59a459315f4c',
                 'http://160.40.52.200:8084/Ansibles/045b57b7-2a2b-4490-98b1-764516af2a65',
                 'http://160.40.52.200:8084/Ansibles/a9ffd599-fb40-4a19-a9d6-30db5407d1ae',
                 'http://160.40.52.200:8084/Ansibles/b4cc6090-4790-468d-9e7b-8d6ce85e0424',
                 'http://160.40.52.200:8084/Ansibles/f7913d15-7974-4241-99b3-cfd6d0ec793b',
                 'http://160.40.52.200:8084/Ansibles/d60fe710-7d65-4cca-aa8e-737eab3e3a26',
                 'http://160.40.52.200:8084/Ansibles/2461b289-4435-4031-a999-1de0d0a6c5ff',
                 'http://160.40.52.200:8084/Ansibles/520afe9e-b083-444e-9b93-74765c7e90ac',
                 'http://160.40.52.200:8084/Ansibles/f7180043-ff5f-4693-be05-014f90b7977c',
                 'http://160.40.52.200:8084/Ansibles/acbb3d50-f145-4279-91e9-be4d0aa5733a',
                 'http://160.40.52.200:8084/Ansibles/08fae0a3-5b2b-421e-b61f-c5a97e43e07d',
                 'http://160.40.52.200:8084/Ansibles/73b225c6-0cdd-4f77-8345-8702e3535322',
                 'http://160.40.52.200:8084/Ansibles/5341320a-25ea-4b47-9fa9-afa7528da585',
                 'http://160.40.52.200:8084/Ansibles/7c81cd34-aa8e-4666-a978-c874557278fe',
                 'http://160.40.52.200:8084/Ansibles/6aedac32-1dd9-445d-8e05-5d02bcf8e580'],

                ['2d57b396-0e23-479e-972e-49f1ee33417c_configure_demo.yml',
                 'e8f67cde-c4b5-4beb-94a8-5c08e94cac22_vm_create.yml',
                 '3828dab9-220f-4f38-b425-59a459315f4c_vm_delete.yml',
                 '045b57b7-2a2b-4490-98b1-764516af2a65_add_container.yml',
                 'a9ffd599-fb40-4a19-a9d6-30db5407d1ae_remove_container.yml',
                 'b4cc6090-4790-468d-9e7b-8d6ce85e0424_add_network.yml',
                 'f7913d15-7974-4241-99b3-cfd6d0ec793b_remove_network.yml',
                 'd60fe710-7d65-4cca-aa8e-737eab3e3a26_security_rule_create.yml',
                 '2461b289-4435-4031-a999-1de0d0a6c5ff_security_rule_delete.yml',
                 '520afe9e-b083-444e-9b93-74765c7e90ac_add_volume.yml',
                 'f7180043-ff5f-4693-be05-014f90b7977c_remove_volume.yml',
                 'acbb3d50-f145-4279-91e9-be4d0aa5733a_create_docker_host.yml',
                 '08fae0a3-5b2b-421e-b61f-c5a97e43e07d_delete_docker_host.yml',
                 '73b225c6-0cdd-4f77-8345-8702e3535322_add_cert.yml',
                 '5341320a-25ea-4b47-9fa9-afa7528da585_remove_cert.yml',
                 '7c81cd34-aa8e-4666-a978-c874557278fe_login_user.yml',
                 '6aedac32-1dd9-445d-8e05-5d02bcf8e580_logout_user.yml'],

                ['http://160.40.52.200:8084/Ansibles/e008e756-1380-4c85-acb2-91f34ea3115d',
                 'http://160.40.52.200:8084/Ansibles/93e3668b-2edd-4a4a-8f9a-999213d14a40'],

                ['config.json.tmpl', 'ca.crt'])

    with open('test/fixture.json') as f:
        t = json.load(f)
        parsed_data = parse(t)
        print(parsed_data)
        assert parsed_data == expected
