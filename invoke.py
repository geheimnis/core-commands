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

<OPERAND> may be 'run', 'query', or 'optimize'.

When <OPERAND> is 'query', [ARGUMENTS] is a string of Result-ID.
When <OPERAND> is 'run', [ARGUMENTS] are instructions of running an actual
command.
When <OPERAND> is 'optimize', [ARGUMENTS] will be ignored. Old results, which
is older as 60 seconds, will be deleted. Currently we do not put this number
into config file.

Arguments <DATABASE-ACCESS-KEY>, [ARGUMENTS] are encoded in HEX.
"""

CONFIG_TABLE = 'invoke/process_result'
CONFIG_RESULT_LIFE = 60

if __name__ == '__main__':
    import subprocess
    import sys
    import os
    import json
    import time

    from _geheimnis_ import get_database, get_uuid, output_formator

    output = output_formator()

    try:
        if len(sys.argv) < 4:
            raise Exception()

        user_identifier, db_access_key_hex, operand = \
            sys.argv[1:4]
        arguments_raw = ''.join(sys.argv[4:])
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
        query_result = database.get(CONFIG_TABLE, arguments_raw)
        if query_result == None:
            output.error('No result.', 404)
        else:
            output.result(json.dumps(query_result), 200)
        exit()

    elif operand == 'run':
        try:
            arguments = arguments_raw.decode('hex')
        except:
            output.error('Invalid argument.')
            exit()

        new_id = get_uuid(arguments)
        subprocess.Popen(\
            [\
                'python',
                os.path.join(base_path, '_invoke_.py'),
                user_identifier,
                db_access_key_hex,
                new_id,
                arguments_raw,
            ]\
        )
        output.result(new_id, 200)

    elif operand == 'optimize':
        data_list = database.get(CONFIG_TABLE)
        deadline = time.time() - CONFIG_RESULT_LIFE
        delete_keys = []
        for each in data_list:
            if data_list[each]['time'] < deadline:
                delete_keys.append(each)
        for key in delete_keys:
            database.remove(CONFIG_TABLE, key)

    else:
        output.error('Unrecognized operand.', 405)
        exit()
