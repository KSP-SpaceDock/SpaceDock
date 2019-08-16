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
        return config.get(section, key)


_cfg = lambda k: get_env_var_or_config(env, k)
_cfgi = lambda k: int(_cfg(k))
_cfgb = lambda k: strtobool(_cfg(k)) == 1
_cfgl = lambda k: ast.literal_eval(_cfg(k))

logging.config.fileConfig('logging.ini', disable_existing_loggers=True)
site_logger = logging.getLogger(_cfg('site-name'))
