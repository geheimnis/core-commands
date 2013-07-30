#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Codebook Management
===================

Description
-----------
This program implements all necessary operations in managing codebooks.
Codebook is the core of our cipher system, which contains a lot of information
that can be used to make up keys for symmetric ciphers.

Codebooks are managed within the core command system. Exchanging codebooks,
however, can be done by external plugins, e.g. asymmetric cipher, quantum
communication, or direct cable connection to a random number generator
cooperating with another cipher device.

Therefore here codebooks are not generated. They can be added, with a user ID,
credentials, description and max used times. They can be deleted. They can be
queried, resulting in an access ID, descriptions, etc. The credentials in
a codebook will not be revealed, and can be only used by other core commands
to encrypt or decrypt messages.

The codebook manager cooperates with Global Key Management System, which
provides a decrypting key to database. The database should always stored
encrypted.
"""
import os
import sys

from crypt import xipher

class codebook_manager:

    _database = None
    _database_cryptor = None

    def __init__(self, path_to_database, database_access_key):
        """Initialize Codebook Manager.

        This will load the database, if path exists. If not, will try to
        create and initialize that. Database Access Key will be used to
        decrypt the database global encrypting key, a value stored in
        database, or when initializing, encrypt the new database global
        encrypting key."""
        cryptor = xipher(database_access_key)

        create_db = True
        if os.path.isfile(path_to_database):
            try:
                # Attempt to load the database.
                self._database = shelve.open(
                    path_to_database,
                    writeback=True,
                    flag='rw',
                )
                create_db = False
            except:
                pass
        if create_db == True:
            # Create a database.
            self._database = shelve.open(
                path_to_database,
                writeback=True,
                flag='n',
            )
            # Pick a random database encrypting key.
            database_encrypt_key = \
                ''.join(chr(random.randint(0,255)) for i in xrange(256))
            # Encrypt the above key using 'database_access_key'.
            encrypted_key = xipher.encrypt(database_encrypt_key)
            # Save the encrypted above key in our new database.
            self._database['options'] = {'key': encrypted_key}
            self._database['books'] = {}
        else:
            try:
                database_encrypt_key = xipher.decrypt(
                    self._database['options']['key']
                )
            except:
                raise RuntimeError('Failed to decrypt database.')

        # Set up encryptor
        self._database_cryptor = xipher(database_encrypt_key)
        # Clear database access key
        database_access_key = None
        database_encrypt_key = None
        del database_access_key, database_encrypt_key

    def add(self, user_id, credentials, description='', max_usage=False):
        pass

    def delete(self, codebook_id):
        pass

    def query(self, user_id):
        pass

    def key_new(self, codebook_id):
        """Read a codebook and make up a new key.

        The codebook ID must be provided. Then a new key is generated basing
        on randomly look up in this codebook. The usage counter is increased.

        Returns a tuple: (KeyValue, Hints), where KeyValue is the new key, and
        Hints a string indicating how this key can be reconstructed
        accordingly."""
        pass

    def key_reconstruct(self, hints):
        """Reconstruct a key.

        Basing on the hints specified, this function trys to reconstruct
        a key. The information in 'hints' is used to look up the database
        and to construct a key. This may not always succeed, while we may not
        have the proper codebook.

        Returns a string, when key successfully reconstructed.
        Raises Exceptions, when key reconstruct process cannot be
        accomplished."""
        pass

if __name__ == '__main__':
    pass
