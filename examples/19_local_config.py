"""
Example 19
Local config test
"""

import configparser
import tempfile

import pyexasol as E
import _config as config

import pprint
printer = pprint.PrettyPrinter(indent=4, width=140)

# Generate tmp file with sample config
handle = tempfile.NamedTemporaryFile('w+')
parser = configparser.ConfigParser()

parser['test1'] = {
    'dsn': config.dsn,
    'user': config.user,
    'password': config.password,
    'schema': config.schema,
    'compression': True,
    'encryption': False,
    'socket_timeout': 20
}

parser.write(handle)
handle.seek(0)

print(handle.read())

# Open connection using config file
C = E.connect_local_config('test1', config_path=handle.name)

# Basic query
stmt = C.execute("SELECT * FROM users ORDER BY user_id LIMIT 5")
printer.pprint(stmt.fetchall())

# Disconnect
C.close()
handle.close()
