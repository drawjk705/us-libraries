import json
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from us_pls._config import Config
from us_pls._persistence.on_disk_cache import CacheException, OnDiskCache

default_config = Config(2019)


@pytest.fixture(autouse=True)
def mock_rmtree(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(shutil, "rmtree")


@pytest.fixture(autouse=True)
def mock_os_remove(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(os, "remove")


@pytest.fixture(autouse=True)
def mock_os_rename(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(os, "rename")


@pytest.fixture(autouse=True)
def mock_json_dump(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(json, "dump")


@pytest.fixture(autouse=True)
def mock_json_load(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(json, "load")


@pytest.fixture(autouse=True)
def mock_open(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("builtins.open")


@pytest.fixture(autouse=True)
def mock_path_exists(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(Path, "exists")


@pytest.fixture(autouse=True)
def mock_path_mkdir(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(Path, "mkdir")


@pytest.fixture(autouse=True)
def mock_path_is_dir(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(Path, "is_dir")


def get_cache(config: Config = default_config) -> OnDiskCache:
    return OnDiskCache(config=config, logger_factory=MagicMock())


@pytest.mark.parametrize("should_overwrite_existing_cache", [True, False])
def test_cache_init(
    should_overwrite_existing_cache: bool,
    mock_path_mkdir: MagicMock,
    mock_rmtree: MagicMock,
):
    default_config = Config(
        2019, should_overwrite_existing_cache=should_overwrite_existing_cache
    )

    _ = get_cache(default_config)

    if should_overwrite_existing_cache:
        mock_rmtree.assert_called_once()
    else:
        mock_rmtree.assert_not_called()

    mock_path_mkdir.assert_called_once()


@pytest.mark.parametrize("path_exists", [True, False])
def test_exists(path_exists: bool, mock_path_exists: MagicMock):
    mock_path_exists.return_value = path_exists

    assert get_cache().exists("banana") == path_exists


@pytest.mark.parametrize("resource_path", ["data/2019/banana", "banana"])
def test_get_full_path_name(resource_path: str):
    assert get_cache()._get_full_path(Path(resource_path)) == Path("data/2019/banana")


def test_put_bytes(mock_open: MagicMock):
    get_cache().put(bytes([1, 2, 3]), "somwhere")

    mock_open.assert_called_once_with(Path("data/2019/somwhere"), "wb")


def test_put_json(mock_open: MagicMock, mock_json_dump: MagicMock):
    get_cache().put(dict(some="thing"), "somewhere")

    mock_open.assert_called_once_with(Path("data/2019/somewhere"), "w")
    mock_json_dump.assert_called_once()


def test_get_miss(mock_path_exists: MagicMock):
    mock_path_exists.return_value = False

    assert get_cache().get("something", "txt") is None


def test_get_json(
    mock_path_exists: MagicMock,
    mock_json_load: MagicMock,
    mock_open: MagicMock,
    mock_read_csv: MagicMock,
):
    mock_path_exists.return_value = True

    get_cache().get("something", "json")

    mock_open.assert_called_once_with(Path("data/2019/something"), "r")
    mock_json_load.assert_called_once()
    mock_read_csv.assert_not_called()


def test_get_txt(
    mock_path_exists: MagicMock,
    mock_open: MagicMock,
    mock_json_load: MagicMock,
    mock_read_csv: MagicMock,
):
    mock_path_exists.return_value = True

    get_cache().get("something", "txt")

    mock_open.assert_called_once_with(Path("data/2019/something"), "r")
    mock_json_load.assert_not_called()
    mock_read_csv.assert_not_called()


def test_get_df(
    mock_path_exists: MagicMock,
    mock_read_csv: MagicMock,
    mock_json_load: MagicMock,
    mock_open: MagicMock,
):
    mock_path_exists.return_value = True

    get_cache().get("something", "df")

    mock_read_csv.assert_called_once_with(Path("data/2019/something"))
    mock_json_load.assert_not_called()
    mock_open.assert_not_called()


def test_get_bad_type(mock_path_exists: MagicMock):
    mock_path_exists.return_value = True

    with pytest.raises(
        CacheException,
        match='resource_type "banana" does not match "json", "txt" or "df"',
    ):
        get_cache().get("somewhere", "banana")  # type: ignore


@pytest.mark.parametrize("is_dir", [True, False])
def test_remove(
    is_dir: bool,
    mock_rmtree: MagicMock,
    mock_os_remove: MagicMock,
    mock_path_is_dir: MagicMock,
):
    mock_path_is_dir.return_value = is_dir

    get_cache().remove(Path("path"))

    if is_dir:
        mock_rmtree.assert_called_once_with(Path("data/2019/path"))
        mock_os_remove.assert_not_called()
    else:
        mock_rmtree.assert_not_called()
        mock_os_remove.assert_called_once_with(Path("data/2019/path"))


def test_rename(mock_os_rename: MagicMock):
    get_cache().rename(Path("a"), Path("b"))

    mock_os_rename.assert_called_once_with(Path("data/2019/a"), Path("data/2019/b"))
