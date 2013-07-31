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
import math
import os
import random
import shelve
import sys

import msgpack

from crypt import xipher
from hash import hash_generator

class codebook_manager:

    _database = None
    _database_cryptor = None
    _hasher = hash_generator()

    # Min and max length of a codebook.
    CODEBOOK_MIN_LENGTH = 1024          #  1 kB
    CODEBOOK_MAX_LENGTH = 10485670      # 10 MB

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

    def add(self, user_id, credentials, description='', max_usage=False):
        """Add a codebook.

        'user_id' should be a HEX-coded identifier. 'credentials' is the very
        confidential data in this codebook in plaintext. 'max_usage' set to
        False, indicating infinitive usage or a integer > 0 to limit the times
        of usage."""
        if not self._database['books'].has_key(user_id):
            self._database['books'] = {user_id: {}}

        if user_id.lower().translate(None,'0123456789abcdef') != '':
            raise RuntimeError('Invalid user ID. Must be HEX formatted.')

        if not (
            (max_usage == False) or
            (type(max_usage) == int and max_usage > 0)):
            raise RuntimeError(
                'Usage specification invalid in adding Codebook.'
            )

        codebook_length = len(credentials)
        if codebook_length > self.CODEBOOK_MAX_LENGTH or \
            codebook_length < self.CODEBOOK_MIN_LENGTH:
            raise RuntimeError('Improper codebook length.')

        codebook_id =\
            user_id + '-' +\
            hash_generator().option({
                'algorithm': 'SHA-1',
                'output_format': 'HEX',
            }).digest(credentials)
        codebook_id = codebook_id.upper()

        if self._database['books'][user_id].has_key(codebook_id):
            raise Exception('Codebook exists.')

        piece_key = ''.join(chr(random.randint(0,255)) for i in xrange(256))
        piece_key_encrypted = self._database_cryptor.encrypt(piece_key)
        insert_piece = {
            'credentials': xipher(piece_key).encrypt(credentials),
            'encrypt_key': piece_key_encrypted,
            'length': codebook_length,
            'description': description,
            'max_usage': max_usage,
            'usage': 0,
        }
        self._database['books'][user_id][codebook_id] = insert_piece

        piece_key, insert_piece = None, None
        del piece_key, insert_piece

    def delete_codebook(self, codebook_id):
        try:
            user_id = self._get_user_id(codebook_id)
            if self._database['books'].has_key(user_id):
                del self._database['books'][user_id][codebook_id]
        except:
            return False
        return True

    def delete_user(self, user_id):
        try:
            if self._database['books'].has_key(user_id):
                del self._database['books'][user_id]
        except:
            return False
        return True

    def query(self, user_id=None):
        """Query user ids or code books.

        When user_id is a string, query this user and try to list all his
        codebooks. Otherwise list just all the users."""
        if type(user_id) == str:
            if self._database['books'].has_key(user_id):
                retval = {}
                for codebook_id in self._database['books'][user_id]:
                    codebook = self._database['books'][user_id][codebook_id]
                    retval[codebook_id] = {
                        'description': codebook['description'],
                        'usage': codebook['usage'],
                        'max_usage': codebook['max_usage'],
                        'length': codebook['length'],
                    }
                return retval
            else:
                return False
        else:
            return self._database['books'].keys()

    def key_new(self, codebook_id, parts=4, key_bytes=128):
        """Read a codebook and make up a new key.

        The codebook ID must be provided. Then a new key is generated basing
        on randomly look up in this codebook. The usage counter is increased.

        Returns a tuple: (KeyValue, Hints), where KeyValue is the new key, and
        Hints a string indicating how this key can be reconstructed
        accordingly."""
        try:
            user_id = self._get_user_id(codebook_id)
            codebook = self._database['books'][user_id][codebook_id]
        except:
            raise Exception('Unable to locate this codebook to get keys.')

        piece_key = self._database_cryptor.decrypt(codebook['encrypt_key'])
        credentials = codebook['credentials']
        total_length = codebook['length']

        part_length = int(math.ceil(key_bytes * 1.0 / parts))
        divide_parts = int(math.floor(total_length * 0.5 / part_length))
        used_parts = random.sample(xrange(divide_parts), parts)
        decryptor = xipher(piece_key)
        hints = [codebook_id, key_bytes,]
        raw_key = ''
        for i in used_parts:
            offset = i * part_length + random.randint(0, part_length)
            raw_key += decryptor.decrypt_partial(
                credentials,
                offset,
                offset+part_length)
            hints.append((offset, part_length))

        raw_key = raw_key[:key_bytes]

        decryptor, piece_key = None, None
        del decryptor, piece_key

        self._database['books'][user_id][codebook_id]['usage'] += 1
        return (raw_key, msgpack.packb(hints))

    def key_reconstruct(self, hints):
        """Reconstruct a key.

        Basing on the hints specified, this function trys to reconstruct
        a key. The information in 'hints' is used to look up the database
        and to construct a key. This may not always succeed, while we may not
        have the proper codebook.

        Returns a string, when key successfully reconstructed.
        Raises Exceptions, when key reconstruct process cannot be
        accomplished."""
        try:
            raw_key = ''
            hints = msgpack.unpackb(hints)
            codebook_id = hints.pop(0)
            key_bytes = hints.pop(0)

            user_id = self._get_user_id(codebook_id)
            codebook = self._database['books'][user_id][codebook_id]

            piece_key = self._database_cryptor.decrypt(
                codebook['encrypt_key']
            )
            decryptor = xipher(piece_key)

            for hint in hints:
                part_offset = hint[0]
                part_length = hint[1]
                key_part = decryptor.decrypt_partial(
                    codebook['credentials'],
                    part_offset,
                    part_offset + part_length
                )
                raw_key += key_part
            raw_key = raw_key[:key_bytes]
        except Exception,e:
            decryptor, piece_key = None, None
            del decryptor, piece_key
            print e
            raise RuntimeError('Unable to reconstruct the key.')

        decryptor, piece_key = None, None
        del decryptor, piece_key

        self._database['books'][user_id][codebook_id]['usage'] += 1
        return raw_key

    def _get_user_id(self, codebook_id):
        user_id_find = codebook_id.find('-')
        if user_id_find >= 0:
            return codebook_id[:user_id_find]
        else:
            return False

if __name__ == '__main__':
    x = codebook_manager('test','test')
#    print x.query('001')

#    x.add('001',''.join(chr(random.randint(0,255)) for i in xrange(1024)),'Hello')

    got = x.query('001')

    print got
"""
    raw_key, hints = x.key_new(got.keys()[0])

    rk2 = x.key_reconstruct(hints)
    print repr(hints)

    print rk2 == raw_key
    print rk2.encode('hex')"""
