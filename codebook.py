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

    def __init__(self, path_to_database, database_encrypt_key):
        pass

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

        Returns a string, when key successfully reconstructed. Returns False,
        when we can not complete this process."""
        pass

if __name__ == '__main__':
    pass
