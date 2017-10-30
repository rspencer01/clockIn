##
# @namespace config
#
# System used for loading configurations from files.
import os

import web.utils

# Creates a dictionary object out of a configuration file
#
# Creates a dictionary out of configuration files.  Config
# files should have extension `.cfg` and format
#
#     name : "someString"
#     age  : someLiteral
#     list : ['A','list','of','items']
#     # A commented line.
#
# If the name of the configuration file is not specified,
# the default is `options.cfg`.


def get_configuration(config_file='options.cfg'):
    with open(config_file, 'r') as config_file:
        lines = [line[:-1] for line in config_file.readlines()]

    config_storage = web.utils.Storage()

    for index, line in enumerate(lines):
        line = line.strip()

        if not line.split():
            continue

        if line.startswith('#'):
            continue

        line = line.split(':')
        config_storage[line[0].strip()] = eval(':'.join(line[1:]))

    return config_storage


CLOCK_IN_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE_CONFIG_FILE_PATH = os.path.join(
    CLOCK_IN_DIR,
    'config',
    'database.cfg'
)

DB_CONF = get_configuration(DATABASE_CONFIG_FILE_PATH)


# Execute a module test
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        print get_configuration(sys.argv[1])
    else:
        print get_configuration()
