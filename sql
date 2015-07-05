#! /usr/bin/python
import sys
import os
import config
# Grab the database configuration
configuration = config.get_configuration('config/database.cfg')
# Make a dummy file, called 't', and write the arguments to this
a = open('t', 'w')
a.write(' '.join(sys.argv[1:]))
a.close()
# Execute the MySQL.
os.system('mysql -u {user} --password={pw} {db} -t < t'.format(**configuration))
# Remove our temporary file
os.remove('t')
