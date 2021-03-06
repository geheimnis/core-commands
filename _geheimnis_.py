#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import math
import os
import uuid
import random
import shelve
import sys

import msgpack

from crypt import xipher
from hash import hash_generator

"""
{
    options: {
        key: GENERIC ENCRYPTING KEY - ENCRYPTED USING ACCESS KEY WHEN LOADING
             DATABASE.
    },
    tables: {
        identities: {
            ID_1: HASHED FROM IDENTITY INFORMATION.
            {
                name: ...,

            },
            ID_2: {...},
        },
        codebooks: {
            ID_1: HASHED FROM CODEBOOK INFORMATION.
            {
                identityID: ...,
                validFrom: ...,
                validTo: ...,
                credentials: ...........................,
                usage: ...,
            },
            ID_2: {...},
        },
        pki: {
            keypairs: {
            },
            signatures: {
            }
        }
    }
}
"""
class output_formator:
    
    def result(self, result, code=''):
        self._leader_output(result, '+' + str(code))

    def error(self, error, code=''):
        self._leader_output(error, 'X' + str(code))

    def _leader_output(self, text, leader):
        text = str(text)
        print '\n'.join([('[%s] ' % leader) + i for i in text.split('\n')])


class _database:

    _database = None
    _database_cryptor = None
    _hasher = hash_generator()

    def __init__(self, uri, access_key):
        cryptor = xipher(access_key)

        create_db = True
        if os.path.isfile(uri):
            try:
                # Attempt to load the database.
                self._database = shelve.open(
                    uri,
                    writeback=True,
                    flag='rw',
                )
                create_db = False
            except:
                pass
        if create_db == True:
            # Create a database.
            self._database = shelve.open(
                uri,
                writeback=True,
                flag='n',
            )
            # Pick a random database encrypting key.
            database_encrypt_key = \
                ''.join(chr(random.randint(0,255)) for i in xrange(256))
            # Encrypt the above key using 'access_key'.
            encrypted_key = \
                xipher(access_key).encrypt(database_encrypt_key)
            # Save the encrypted above key in our new database.
            self._database['options'] = {'key': encrypted_key}
            self._database['tables'] = {}
        else:
            try:
                database_encrypt_key = xipher(access_key).decrypt(
                    self._database['options']['key']
                )
            except Exception,e:
                raise RuntimeError(
                    'Failed to decrypt database. %s' % e
                )
        self._database_cryptor = xipher(database_encrypt_key)

        # Clear keys
        access_key, database_encrypt_key = None, None
        del access_key, database_encrypt_key

    def encrypt(self, plaintext):
        return self._database_cryptor.encrypt(plaintext)

    def decrypt(self, ciphertext):
        return self._database_cryptor.decrypt(ciphertext)

    def set(self, table_path, key, value):
        self._touch_path(table_path)[key] = value
        return self

    def get(self, table_path, key=None):
        table = self._touch_path(table_path)
        if key == None:
            return table
        if not table.has_key(key):
            return None
        return table[key]

    def remove(self, table_path, key):
        table = self._touch_path(table_path)
        if table.has_key(key):
            del table[key]
        return self

    def clear(self, table_path):
        table = self._touch_path(table_path)
        table = {}
        return self

    def _touch_path(self, table_path):
        tree = table_path.split('/')
        for each in tree:
            if each == '':
                raise RuntimeError('Invalid table access path.')

        root = self._database['tables']
        for each in tree:
            if not root.has_key(each):
                root[each] = {}
            root = root[each]

        return root


### initialize everything ###

#  Read ini
BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
ini_relpath = open(os.path.join(BASEPATH, 'confpath.dat'), 'r').read().strip()
ini_realpath = os.path.realpath(os.path.join(BASEPATH, ini_relpath))
ini_basedir = os.path.dirname(ini_realpath)

config = ConfigParser.ConfigParser()
config.read(ini_realpath)

path_databases = os.path.realpath(
    os.path.join(
        ini_basedir,
        config.get('path', 'databases')
    )
)

if not path_databases.startswith(ini_basedir):
    raise RuntimeError(
        'Database storage path is not within config file container.'
    )

# Initialize database loader
def get_database(user_identity, access_key):
    user_identifier = user_identity.get_id()
    uri = os.path.realpath(os.path.join(path_databases, user_identifier))
    if not uri.startswith(path_databases):
        raise RuntimeError(
            'Invalid user identifier specified.'
        )
    return _database(uri, access_key)

# def UUID generator
def get_uuid(chaos=''):
    u4 = uuid.uuid4()
    u5 = uuid.uuid5(u4, chaos)
    u1 = uuid.uuid1()

    u3 = uuid.uuid3(u5, str(u1))
    return str(u3)
