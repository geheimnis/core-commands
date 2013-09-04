#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Identity Management System
==========================

Synopsis
--------
python identity.py \
    <USER_IDENTIFIER> <DATABASE_ACCESS_KEY> <OPERAND> [ARGUMENTS]

<USER_IDENTIFIER> is used to select the right database. Maybe only a
HEX-Encoded string not longer than 128 characters.

<DATABASE_ACCESS_KEY> is a HEX-Encoded string, used to open the database.

<OPERAND> must be one of the followings:
    list    List all stored identities under this user.
    add     Examine and insert a new identity, which takes [ARGUMENTS] as
            configuration of this new identity.
    test    Like 'add', but not actually add this identity, only test and
            gives out ID, for examination.
    delete  [ARGUMENTS] here is the target identity's ID.

Description
-----------
1. list

"""
import json

from hash import object_hasher

class identity:

    _title, _describe = '',''

    _loaded = False

    def __init__(self, init_string=None):
        if init_string != None:
            self.load_string(init_string)

    def initialize(self, title, describe):
        """Create a new identity.

        Arguments:

        title       size: [5, 30], a title of this new identity.
        describe    size: [0, 140], a brief description.

        All above item values are limited to a charset with:
            a-z A-Z 0-9 _@#/\.:=+
        """
        title = title.strip()
        describe = describe.strip()

        test_result = self._test_data(title, describe)
        if test_result == False: return False

        self._title, self._describe = test_result
        self._loaded = True

    def _test_data(self, title, describe):
        passed = (
            (self._filter_string(title) in xrange(5,31)) and
            (self._filter_string(describe) in xrange(0,141))
        )

        if passed == True:
            return title, describe
        else:
            return False

    def load_string(self, string):
        try:
            string = json.loads(string)
            title = string['title']
            describe = string['describe']
            
            self.initialize(
                title,
                describe,
            )

        except Exception,e:
            raise RuntimeError('Failed to load given identity data.')

    def __str__(self):
        if not self._loaded:
            return ''
        else:
            ret = json.dumps({
                'title': self._title,
                'describe': self._describe,
            })
            return ret

    def get_id(self):
        if not self._loaded: return
        hasher = object_hasher('SHA-1')
        return hasher.hash(self.__str__()).encode('hex')

    def _filter_string(self, string):
        try:
            ret = len(string)
            for i in 'abcdefghijklmnopqrstuvwxyz0123456789_@#/\.:=+':
                string = string.replace(i, '')
            if string == '':
                return ret
            else:
                return None
        except Exception,e:
            return None

if __name__ == '__main__':
    import sys

    import json

    from _geheimnis_ import get_database, output_formator

    output = output_formator()

    try:
        user_identifier, db_access_key, operand = sys.argv[1:4]
        argument = ''
        if len(sys.argv) > 4:
            argument = ' '.join(sys.argv[4:]).decode('hex')
    except Exception,e:
        output.error("Usage: python identity.py " +\
            "<USER_IDENTIFIER> <DB_ACCESS_KEY> <OPERAND> [ARGUMENTS]")
        exit()

    try:
        db_access_key = db_access_key.decode('hex')
        database = get_database(user_identifier, db_access_key)
    except Exception,e:
        output.error('Cannot connect to database. Reason: %s' % e, 401)
        exit()

    operand = operand.strip().lower()

    if operand == 'list':
        result = database.get('identities')
        output.result(
            json.dumps(
                result.keys()
            )
        )

    elif operand == 'delete':
        database.remove('identities', argument)
        output.result('Deleted.', 200)

    elif operand in ['add', 'test']:
        try:
            new_id_instance = identity(argument)
        except Exception,e:
            output.error('Error reading input: %s' % e, 400)
            exit()

        try:
            new_id = new_id_instance.get_id()
            new_id_string = str(new_id_instance)

            if type(new_id) != str:
                raise Exception(
                    'Invalid parameters. Cannot be loaded.'
                )
            
            if operand == 'add':
                if new_id != '':
                    database.set('identities', new_id, new_id_string)
                else:
                    raise Exception(
                        'Identity not loaded out of unknown reason.'
                    )
            else:
                output.result(new_id, 201)
        except Exception,e:
            output.error('Error saving identity: %s' % e, 500)
            exit()

    else:
        output.error('Unrecognized operand.', 405)
        exit()
