import pytest

from src.main import get_access_token, get_api_key, get_project_domain, XoperaConfig


class TestMain:
    def test_get_token(self, mocker):
        mock = mocker.MagicMock()
        mock.headers = {"Authorization": "Bearer TEST_TOKEN"}
        token = get_access_token(mock)
        assert token == "TEST_TOKEN"

        mock.headers = {}
        token = get_access_token(mock)
        assert token == None

        mock.headers = {"Authorization": "BearerTEST_TOKEN"}
        token = get_access_token(mock)
        assert token == None

        mock.headers = {"Authorization": "None TEST_TOKEN"}
        token = get_access_token(mock)
        assert token == None

    def test_get_api_key(self, mocker):
        mock = mocker.MagicMock()
        mock.headers = {XoperaConfig.get_xopera_api_key_header(): "TEST_KEY"}
        token = get_api_key(mock)
        assert token == "TEST_KEY"

        mock.headers = {}
        token = get_api_key(mock)
        assert token == None

        mock.headers = {"Authorization": "TEST_KEY"}
        token = get_api_key(mock)
        assert token == None
 
    def test_get_project_domain(self, mocker):
        json_aadm = { "test": "test", "test2": {"type": "AbstractApplicationDeploymentModel", "namespace": "test"} }      
        domain = get_project_domain(json_aadm)
        assert domain == "test"

        json_aadm = { "test": "test", "test2": {"namespace": "test"} }      
        domain = get_project_domain(json_aadm)
        assert domain == None

        json_aadm = { "test": "test" }      
        domain = get_project_domain(json_aadm)
        assert domain == None          
