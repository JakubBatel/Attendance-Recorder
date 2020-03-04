import configparser
from pkg_resources import resource_filename

config = configparser.ConfigParser()
config.read(resource_filename(__name__, 'config.ini'))
