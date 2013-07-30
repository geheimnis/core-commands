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

Therefore here codebooks are not generated. They can be added, with details
and description and validity time period. They can be deleted. They can be
queried, resulting in an access ID, descriptions, etc. The credentials in
a codebook will not be revealed, and can be only used by other core commands
to encrypt or decrypt messages.

The codebook manager cooperates with Global Key Management System, which
provides decrypting keys to database.
"""
import os
import sys

from crypt import xipher

class codebook_manager:

    def __init__(self, path_to_database, database_key):
        pass

if __name__ == '__main__':
    pass
