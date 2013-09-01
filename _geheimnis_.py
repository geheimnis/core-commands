#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import os
import random
import shelve
import sys

import msgpack

from crypt import xipher
from hash import hash_generator

class database:

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
            # Encrypt the above key using 'database_access_key'.
            encrypted_key = \
                xipher(database_access_key).encrypt(database_encrypt_key)
            # Save the encrypted above key in our new database.
            self._database['options'] = {'key': encrypted_key}
            self._database['books'] = {}
        else:
            try:
                database_encrypt_key = xipher(database_access_key).decrypt(
                    self._database['options']['key']
                )
            except Exception,e:
                print e
                raise RuntimeError('Failed to decrypt database.')
        self._database_cryptor = xipher(database_encrypt_key)

        # Clear keys
        database_access_key, database_encrypt_key = None, None
        del database_access_key, database_encrypt_key


