#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Async Generic Command Invoker
=============================

This generic invoker provides a simplified interface to web-interface. It
provides 3 features:
1. Invoke another command, and reserves a Result-ID for the caller.
2. Query the result cache with given Result-ID.
3. Simplify the interface to complex commands.

SYNPOSIS
--------
python invoke.py <USER-IDENTIFIER> <DATABASE-ACCESS-KEY> <OPERAND> [ARGUMENTS]

<OPERAND> may be either 'run' or 'query'.

When <OPERAND> is 'query', <ARGUMENTS> is a string of Result-ID.
When <OPERAND> is 'run', <ARGUMENTS> are instructions of running an actual
command.

Arguments <DATABASE-ACCESS-KEY>, [ARGUMENTS] are encoded in HEX.
"""

if __name__ == '__main__':
    import subprocess
    import sys
    import os
    import random

    from _geheimnis_ import get_database, get_uuid, output_formator

    output = output_formator()

    try:
        if len(sys.argv) < 4:
            raise Exception()

        user_identifier, db_access_key_hex, operand = \
            sys.argv[1:4]
        arguments_hex = ''.join(sys.argv[4:])
        arguments = arguments_hex.decode('hex')
        base_path = os.path.realpath(os.path.dirname(sys.argv[0]))
    except Exception,e:        
        output.error("Usage: python invoke.py <USER-IDENTIFIER>" + \
            "<DATABASE-ACCESS-KEY> <OPERAND> [ARGUMENTS]", 400)
        exit()

    try:
        db_access_key = db_access_key_hex.decode('hex')
        database = get_database(user_identifier, db_access_key)
    except Exception,e:
        output.error('Cannot connect to database. Reason: %s' % e, 401)
        exit()

    operand = operand.strip().lower()

    if operand == 'query':
        query_result = database.get('invoke/process_result', arguments)
        if query_result == None:
            output.error('No result.', 404)
        else:
            output.result(query_result, 200)
        exit()

    elif operand == 'run':
        new_id = get_uuid(arguments)
        subprocess.Popen(\
            [\
                'python',
                os.path.join(base_path, '_invoke_.py'),
                user_identifier,
                db_access_key_hex,
                new_id,
                arguments_hex,
            ]\
        )
        output.result(new_id, 200)                

    else:
        output.error('Unrecognized operand.', 405)
        exit()
