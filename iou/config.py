"""
Configuration interface for iou.

Allows configuration from environment variables.
"""

import logging
import logging.config
from enum import Enum
from importlib.abc import Traversable
from importlib.resources import files
from typing import BinaryIO, List, Pattern, Union

import tomli
from pydantic import AnyHttpUrl, BaseSettings


class Environment(Enum):
    """Runtime environment which configures e.g. certain loggers differently"""

    PROD = "production"
    DEVELOP = "develop"


def load_log_config(config_path: Union[str, Traversable]) -> None:
    """
    Loads configuration from a toml file.

    This configuration file contains a standard Python logging configuration
    dictionary. See [1] for details on the valid settings.

    [1]: https://docs.python.org/3.7/library/logging.config.html#configuration-dictionary-schema
    """
    config_file: BinaryIO
    if isinstance(config_path, Traversable):
        config_file = config_path.open("rb")
    else:
        config_file = open(config_path, "rb")  # pylint: disable=consider-using-with
    log_config = tomli.load(config_file)
    if not log_config:
        logging.warning("Loaded a blank logging config?")
    config_file.close()

    logging.config.dictConfig(log_config)
    if settings.IOU_ENVIRONMENT == Environment.DEVELOP:
        logging.getLogger("root").setLevel(logging.DEBUG)


class Settings(BaseSettings):
    """Primary settings of the app."""

    IOU_SERVER_NAME: str = "iou"
    IOU_SERVER_HOST: str = "127.0.0.1"
    IOU_SERVER_PORT: int = 8000
    IOU_ENVIRONMENT: Environment = Environment.DEVELOP

    IOU_LOG_CONFIG_FILE: Union[str, Traversable] = (
        files("iou") / "log_config.toml"
    )

    # IOU_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200"]'
    # note: in bash json has to be escaped: '[\"http://localhost\"]'
    IOU_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:8000"]
    # IOU_CORS_ORIGIN_REGEX is a pattern string
    # e.g: 'https://.*\.example\.com
    IOU_CORS_ORIGIN_REGEX: Pattern = r"https://.*\.notourserver\.de"

    class Config:
        # pylint: disable=too-few-public-methods
        """Static configuration"""
        case_sensitive = True


settings = Settings()
