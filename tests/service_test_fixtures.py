from typing import Any, Generic, TypeVar, cast
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

_T = TypeVar("_T")


@pytest.mark.usefixtures("inject_mocker_to_class", "service_fixture")
class ServiceTestFixture(Generic[_T]):
    _service: _T
    mocker: MockerFixture

    def cast_mock(self, dependency: Any) -> MagicMock:
        return cast(MagicMock, dependency)


@pytest.mark.usefixtures("api_fixture")
class ApiServiceTestFixture(ServiceTestFixture[_T]):
    requests_get_mock: MagicMock
