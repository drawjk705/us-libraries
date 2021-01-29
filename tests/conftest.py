import inspect
from typing import Dict, cast
from unittest.mock import MagicMock

import pandas
import pytest
import requests
from pytest import FixtureRequest, MonkeyPatch
from pytest_mock.plugin import MockerFixture

from tests import utils

# pyright: reportPrivateUsage=false


# pandas mocks
@pytest.fixture
def mock_read_csv(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(pandas, "read_csv")


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
