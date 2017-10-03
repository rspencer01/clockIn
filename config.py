##
# @namespace config
#
# System used for loading configurations from files.

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
        lines[index] = line.strip()

        if not line.split():
            continue

        if line.startswith('#'):
            continue

        lines[index] = line.split(':')
        config_storage[line.strip()] = eval(':'.join(line[1:]))

    return config_storage


# Execute a module test
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        print get_configuration(sys.argv[1])
    else:
        print get_configuration()
