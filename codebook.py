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
import sys

import msgpack

from crypt import xipher
from hash import hash_generator
from _geheimnis_ import get_database

class codebook_manager:

    _database = None
    _hasher = hash_generator()

    # Min and max length of a codebook.
    CODEBOOK_MIN_LENGTH = 1024          #  1 kB
    CODEBOOK_MAX_LENGTH = 10485670      # 10 MB

    def __init__(self, database):
        """Initialize Codebook Manager."""
        self._database = database

    def add(self, identity, credentials, description='', max_usage=False):
        """Add a codebook.

        'identity' is an instance of identity, 'credentials' is the very
        confidential data in this codebook in plaintext. 'max_usage' set to
        False, indicating infinitive usage or a integer > 0 to limit the times
        of usage."""
        user_id = identity.get_id()

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

        visit_path = 'books/%s' % user_id

        if self._database.get(visit_path, codebook_id) != None:
            raise Exception('Codebook exists.')

        piece_key = ''.join(chr(random.randint(0,255)) for i in xrange(256))
        piece_key_encrypted = self._database.encrypt(piece_key)
        insert_piece = {
            'credentials': xipher(piece_key).encrypt(credentials),
            'encrypt_key': piece_key_encrypted,
            'length': codebook_length,
            'description': description,
            'max_usage': max_usage,
            'usage': 0,
        }
        self._database.set(visit_path, codebook_id, insert_piece)

        piece_key, insert_piece = None, None
        del piece_key, insert_piece

    def delete_codebook(self, codebook_id):
        try:
            user_id = self._get_user_id(codebook_id)
            self._database.remove('books/%s' % user_id, codebook_id) 
        except:
            return False
        return True

    def delete_user(self, identity):
        try:
            user_id = identity.get_id()
            self._database.remove('books', user_id)
        except:
            return False
        return True

    def query(self, identity):
        """Query user ids or code books.

        When user_id is a string, query this user and try to list all his
        codebooks. Otherwise list just all the users."""
        if 'get_id' in dir(identity):
            user_id = identity.get_id()
            user_books = self._database.get('books', user_id)
            if user_books != None:
                retval = {}
                for codebook_id in user_books:
                    codebook = user_books[codebook_id]
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
            return self._database.get('books')

    def key_new(self, codebook_id, parts=4, key_bytes=128):
        """Read a codebook and make up a new key.

        The codebook ID must be provided. Then a new key is generated basing
        on randomly look up in this codebook. The usage counter is increased.

        Returns a tuple: (KeyValue, Hints), where KeyValue is the new key, and
        Hints a string indicating how this key can be reconstructed
        accordingly."""
        try:
            user_id = self._get_user_id(codebook_id)
            codebook = self._database.get('books/%s' % user_id, codebook_id)
        except Exception,e:
            raise Exception('Unable to locate this codebook to get keys.')

        piece_key = self._database.decrypt(codebook['encrypt_key'])
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

        codebook['usage'] += 1
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
            codebook = self._database.get('books/%s' % user_id, codebook_id)

            piece_key = self._database.decrypt(codebook['encrypt_key'])
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

        codebook['usage'] += 1
        return raw_key

    def _get_user_id(self, codebook_id):
        user_id_find = codebook_id.find('-')
        if user_id_find >= 0:
            ret = codebook_id[:user_id_find]
            if ret.lower().translate(None, '0123456789abcdef') != '':
                return False
            return ret
        else:
            return False

if __name__ == '__main__':
    """
    from _geheimnis_ import get_database
    from identity import identity as ID 
    
    db = get_database('0000', 'test')
    me = ID()
    me.initialize('testIdentity','')
    print me.get_id()

    x = codebook_manager(db)

    print x.query(me)
    print 'Now add a key'
    x.add(me,''.join(chr(random.randint(0,255)) for i in xrange(1024)),'Hello')

    got = x.query(me)

    print got

    raw_key, hints = x.key_new(got.keys()[0])

    rk2 = x.key_reconstruct(hints)
    print repr(hints)

    print rk2 == raw_key
    print rk2.encode('hex')
    """
