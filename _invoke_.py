#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Process runner and recorder of 'invoke.py'
==========================================

This piece of program runs a command from 'invoke.py', and records result into
database.

SYNPOSIS
--------
python _invoke_.py <USER-IDENTIFIER> <DATABASE-ACCESS-KEY> <RESULT-SAVE-ID> \
    <ARGUMENTS>

** Direct calling to this program is not encouraged. **
"""
import subprocess
import sys
import os
import random

from _geheimnis_ import get_database

try:
    if len(sys.argv) < 5:
        raise Exception()

    user_identifier, db_access_key, result_save_key = \
        sys.argv[1:4]
    arguments = ''.join(sys.argv[4:]).decode('hex')
    base_path = os.path.realpath(os.path.dirname(sys.argv[0]))

    db_access_key = db_access_key.decode('hex')
    database = get_database(user_identifier, db_access_key)

except Exception,e:
    print e
    exit()

print "_invoke_"
