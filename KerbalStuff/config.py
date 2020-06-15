import ast
import logging.config
import os
from configparser import ConfigParser
from distutils.util import strtobool
from typing import Optional, Dict, Any

# Load the software configuration
config = ConfigParser()
config.read('config.ini')
env = 'dev'


def get_env_var_or_config(section: str, key: str) -> Optional[str]:
    env_var = os.getenv(key.upper().replace('-', '_'))
    if env_var:
        return env_var
    else:
        return config.get(section, key, fallback=None)


def _cfg(k: str) -> Optional[str]:
    return get_env_var_or_config(env, k)


def _cfgi(k: str, default: int = 0) -> int:
    val = _cfg(k)
    return int(val) if val is not None else default


def _cfgb(k: str, default: bool = False) -> bool:
    val = _cfg(k)
    return strtobool(val) == 1 if val is not None else default


def _cfgd(k: str, default: Dict[str, str] = None) -> Dict[str, str]:
    if default is None:
        default = {}
    val = _cfg(k)
    return ast.literal_eval(val) if val is not None else default


logging.config.fileConfig('logging.ini', disable_existing_loggers=True)
site_logger = logging.getLogger(_cfg('site-name'))
