from pathlib import Path
import uuid

import pytest
import os
import shutil


@pytest.fixture
def csar_1():
    return file_data('CSAR-hello_fast.zip')


@pytest.fixture
def csar_2():
    return file_data('CSAR-hello_fast.zip')


@pytest.fixture
def csar_3():
    return file_data('CSAR-hello_fast.zip')


@pytest.fixture
def csar_inputs():
    return file_data('CSAR-hello_inputs.zip')


@pytest.fixture
def inputs_1():
    return file_data('hello_inputs.yaml', file_type='inputs_file')


@pytest.fixture
def inputs_2():
    return file_data('hello_inputs.yaml', file_type='inputs_file')


@pytest.fixture
def csar_corrupt():
    return file_data('CSAR-hello_corrupt.zip')


@pytest.fixture
def csar_empty():
    return file_data('CSAR-empty.zip')


@pytest.fixture
def csar_no_meta():
    return file_data('CSAR-no-meta.zip')


@pytest.fixture
def csar_clean_state():
    return file_data('CSAR-clean-state.zip')


def file_data(file_name, file_type='CSAR'):
    path_to_csar = Path(__file__).parent / 'CSAR' / file_name
    data = {file_type: (open(path_to_csar, 'rb'), file_name)}
    return data


@pytest.fixture
def CSAR_unpacked():
    return Path(__file__).parent / 'CSAR_unpacked'


@pytest.fixture
def get_workdir_path():
    workdir_path = Path(__file__).parent / 'workdir' / str(uuid.uuid4())
    os.makedirs(workdir_path)
    yield workdir_path
    shutil.rmtree(workdir_path)


def pytest_addoption(parser):
    parser.addoption(
        "--online", action="store_true", default=False,
        help="run tests requiring online services to be available (may need additional configuration)"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "online: mark test as requiring an online service")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--online"):
        return

    skip_online = pytest.mark.skip(reason="need --online option to run")
    for item in items:
        if "online" in item.keywords:
            item.add_marker(skip_online)
