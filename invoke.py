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
command. This is a string of JSON format, for example:
    
    {"cmd": "identity-list", "arg": None}


When <OPERAND> is 'optimize', [ARGUMENTS] will be ignored. Old results, which
is older as 60 seconds, will be deleted. Currently we do not put this number
into config file.

Arguments <DATABASE-ACCESS-KEY>, [ARGUMENTS] are encoded in HEX.
"""

CONFIG_TABLE = 'invoke/process_result'
CONFIG_RESULT_LIFE = 60

CONFIG_COMMANDS = {
    'instant': {
        'identity-list': {'domain': 'identity', 'operand': 'list', 'arg': False},
        'identity-test': {'domain': 'identity', 'operand': 'test', 'arg': True},
        'identity-delete': {'domain': 'identity', 'operand': 'delete', 'arg': True},
        'identity-add': {'domain': 'identity', 'operand': 'add', 'arg': True},
        'test-instant': {'domain': 'test', 'operand': 'testOperand', 'arg': False},
    },
    'wait': {
        'test-wait': {'domain': 'test', 'operand': 'testOperand', 'arg': False},
    },
}

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
        output.error("Usage: python invoke.py <USER-IDENTIFIER> " + \
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
            arguments = json.loads(arguments_raw.decode('hex'))
            command_name = arguments['cmd'].lower()
            command_argv = arguments['arg']

            command_profile = {}
            execute_instantly = False
            success_code = 0
            

            if command_name in CONFIG_COMMANDS['instant']:
                execute_instantly = True
                command_profile = CONFIG_COMMANDS['instant'][command_name]

            elif command_name in CONFIG_COMMANDS['wait']:
                execute_instantly = False
                command_profile = CONFIG_COMMANDS['wait'][command_name]

            else:
                raise Exception()
        except:
            output.error('Invalid argument.')
            exit()

        execute_list = [
            'python',
            os.path.join(base_path, command_profile['domain'] + '.py'),
            user_identifier,
            db_access_key_hex,
            command_profile['operand'],
        ]
        if command_profile['arg']:
            execute_list.append(command_argv.encode('hex'))

        if execute_instantly:
            print subprocess.check_output(execute_list)

        else:
            new_id = get_uuid(arguments_raw)
            new_arguments = ' '.join(execute_list).encode('hex')
            subprocess.Popen(\
                [\
                    'python',
                    os.path.join(base_path, '_invoke_.py'),
                    user_identifier,
                    db_access_key_hex,
                    new_id,
                    new_arguments,
                ]\
            )
            output.result(new_id, 202)

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
