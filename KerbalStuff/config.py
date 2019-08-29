import ast
import logging.config
import os
from configparser import ConfigParser
from distutils.util import strtobool

# Load the software configuration
config = ConfigParser()
config.read('config.ini')
env = 'dev'


def get_env_var_or_config(section, key):
    env_var = os.getenv(key.upper().replace('-', '_'))
    if env_var:
        return env_var
    else:
        return config.get(section, key, fallback=None)


def _cfg(k):
    return get_env_var_or_config(env, k)


def _cfgi(k, default = 0):
    val = _cfg(k)
    return int(val) if val is not None else default


def _cfgb(k, default = False):
    val = _cfg(k)
    return strtobool(val) == 1 if val is not None else default


def _cfgl(k, default = {}):
    val = _cfg(k)
    return ast.literal_eval(val) if val is not None else default


logging.config.fileConfig('logging.ini', disable_existing_loggers=True)
site_logger = logging.getLogger(_cfg('site-name'))
