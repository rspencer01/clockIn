## 
# @namespace config
# 
# System used for loading configurations from files.

import os
import web.utils

## Creates a dictionary object out of a configuration file
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
    f = open(config_file, 'r')
    lns = [i[:-1] for i in f.readlines()]
    f.close()
    ans = web.utils.Storage()
    for j in range(len(lns)):
        lns[j] = lns[j].strip()
        if not lns[j].split():
            continue
        if lns[j][0] == '#':
            continue
        lns[j] = lns[j].split(':')
        ans[lns[j][0].strip()] = eval(':'.join(lns[j][1:]))
    return ans

# Execute a module test
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        print get_configuration(sys.argv[1])
    else:
        print get_configuration()
