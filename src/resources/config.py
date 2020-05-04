from configparser import ConfigParser
from pkg_resources import resource_filename

config = ConfigParser()
config.read(resource_filename(__name__, 'config.ini'))
