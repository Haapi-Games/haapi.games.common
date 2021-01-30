"""Tests for haapi.games.common."""
import os
from typing import Dict, Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockFixture

from haapi.games import common
from haapi.games.common.gcp import SecretManager


TEST_CONFIGS: Dict[str, Dict[str, Any]] = {
    "DEFAULT": {
        "OWNER_DISCORD_ID": 120007662510407680,
        "EMBED_COLOR": 0xFFEB3B,
    },
    "TEST": {"HG_API_URL": "", "GAME_CHANNEL_ID": -1},
    "DEV": {
        "HG_API_URL": "http://localhost:8080/v2",
        "GAME_CHANNEL_ID": 793232747383881762,
    },
    "PROD": {
        "HG_API_URL": "https://games-servicew-qterp54lzq-uc.a.run.app/v2",
        "GAME_CHANNEL_ID": 787742301261660180,
    },
}

BASE_PARAMS = [
    pytest.param("", id="'', default_config"),
    pytest.param("TEST", id="TEST, test_config"),
    pytest.param("DEV", id="DEV, dev_config"),
    pytest.param("PROD", id="PROD, prod_config"),
]


def test_get_config_fails_with_no_environment(mocker: MockFixture) -> None:
    """It gets DEFAULT without any environment variables.

    Args:
        mocker: MockFixture
    """
    mocker.patch.dict(os.environ, clear=True)
    check_config = common.get_config(TEST_CONFIGS)
    for key, value in TEST_CONFIGS["DEFAULT"].items():
        assert check_config.get(key) == value


@pytest.mark.parametrize("env_variable", BASE_PARAMS)
def test_get_config_for_environment(mocker: MockFixture, env_variable: str) -> None:
    """It gets config based on environment variable.

    Args:
        mocker: MockFixture
        env_variable: the env variable set
    """
    mocker.patch.dict(os.environ, {"ENVIRONMENT": env_variable})
    check_config = common.get_config(TEST_CONFIGS)
    for key, value in TEST_CONFIGS[
        env_variable if len(env_variable) > 0 else "DEFAULT"
    ].items():
        assert check_config.get(key) == value


@pytest.mark.parametrize("env_variable", BASE_PARAMS)
def test_get_config_case_insensitive(mocker: MockFixture, env_variable: str) -> None:
    """It gets config based on environment variable even lowercase.

    Args:
        mocker: MockFixture
        env_variable: the env variable set lowered
    """
    mocker.patch.dict(os.environ, {"ENVIRONMENT": env_variable.lower()})
    check_config = common.get_config(TEST_CONFIGS)
    for key, value in TEST_CONFIGS[
        env_variable if len(env_variable) > 0 else "DEFAULT"
    ].items():
        assert check_config.get(key) == value


@pytest.mark.parametrize("env_variable", BASE_PARAMS)
def test_get_environment_override(mocker: MockFixture, env_variable: str) -> None:
    """It overrides when environment variables that match are set.

    Args:
        mocker: MockFixture
        env_variable: the env variable set
    """
    mocker.patch.dict(os.environ, {"ENVIRONMENT": env_variable})
    mocker.patch.dict(os.environ, {"DISCORD_SECRET": "TEST"})
    expected_config = TEST_CONFIGS[env_variable if len(env_variable) > 0 else "DEFAULT"]
    expected_config["DISCORD_SECRET"] = "TEST"
    mocker.patch.dict(os.environ, {"RAWG_SECRET": "TEST2"})
    expected_config["RAWG_SECRET"] = "TEST2"
    check_config = common.get_config(TEST_CONFIGS)

    assert "DISCORD_SECRET" in check_config
    assert "RAWG_SECRET" in check_config

    for key, value in expected_config.items():
        assert check_config.get(key) == value


def test_secret_manager(mocker: MockFixture) -> None:
    """It can retrieve a secret.

    Args:
        mocker: MockFixture
    """
    mock_access: MagicMock = mocker.patch(
        "google.cloud.secretmanager.SecretManagerServiceClient",
        autospec=True,
    )

    mock_access.return_value.access_secret_version.return_value.payload.data = (
        "random_test_secret".encode("UTF-8")
    )

    ret_val = SecretManager()._get_secret("test")
    mock_access.assert_called_once_with()
    mock_access.return_value.access_secret_version.assert_called_once_with(name="test")
    assert ret_val == "random_test_secret"
