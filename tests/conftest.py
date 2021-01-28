import inspect
import os
import shutil
from pathlib import Path
from typing import Dict, Generator, cast
from unittest.mock import MagicMock

import pandas
import pytest
import requests
from pytest import FixtureRequest, MonkeyPatch
from pytest_mock.plugin import MockerFixture

from tests import utils

# pyright: reportPrivateUsage=false


# pathlib.Path mocks
@pytest.fixture
def mock_path_mkdir(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(Path, "mkdir")


@pytest.fixture
def mock_path_exists(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(Path, "exists")


# shutil mocks
@pytest.fixture
def mock_rmtree(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(shutil, "rmtree")


# pandas mocks
@pytest.fixture
def mock_read_csv(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(pandas, "read_csv")


# filesystem setup
@pytest.fixture
def set_current_path() -> Generator[None, None, None]:
    parent_path = Path(__file__).parent.absolute()

    os.chdir(parent_path)

    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    temp_dir.mkdir(parents=True, exist_ok=False)

    os.chdir(temp_dir.absolute())

    try:
        yield

    finally:
        os.chdir(parent_path)
        shutil.rmtree(temp_dir.absolute())


@pytest.fixture(autouse=True)
def no_requests(monkeypatch: MonkeyPatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture(scope="function")
def api_fixture(request: FixtureRequest, mocker: MockerFixture):
    request.cls.requests_get_mock = mocker.patch.object(requests, "get")  # type: ignore


@pytest.fixture(scope="function")
def inject_mocker_to_class(request: FixtureRequest, mocker: MockerFixture):
    request.cls.mocker = mocker  # type: ignore


@pytest.fixture(scope="function")
def service_fixture(request: FixtureRequest):
    """
    This mocks all of a service's dependencies,
    instantiates the service with those mocked dependencies,
    and assigns the service to the test class's `_service`
    variable
    """

    req = cast(utils._RequestCls, request)
    obj = req.cls

    service = utils.extract_service(obj)

    dependencies: Dict[str, MagicMock] = {}

    # this lets us see all of the service's constructor types
    for dep_name, dep_type in inspect.signature(service).parameters.items():
        # this condition will be true if the service inherits
        # from a generic class
        if hasattr(dep_type.annotation, "__origin__"):
            dependencies[dep_name] = MagicMock(dep_type.annotation.__origin__)
        else:
            dependencies[dep_name] = MagicMock(dep_type.annotation)

    # we call the service's constructor with the mocked dependencies
    # and set the test class obj's _service attribute to hold this service
    obj._service = service(**dependencies)
