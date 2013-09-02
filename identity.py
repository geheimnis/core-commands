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
    delete  [ARGUMENTS] here is the target identity's ID.
    consult [ARGUMENTS] may be 'contact' or 'recognize'.

Description
-----------
1. list

"""
from hash import object_hasher

class identity:

    _title, _describe, _contact, _recognize = '','',{},{}

    _loaded = False

    def __init__(self, init_string=None):
        if init_string != None:
            self.load_string(init_string)

    def initialize(self, title, describe, **argv):
        """Create a new identity.

        Arguments:

        title       size: [5, 30], a title of this new identity.
        describe    size: [0, 140], a brief description.

        argv        with following possibilities:
            contact     dict(associative array), with recognized keys as
                        listed:
                            phone, mobile, fax, email, addr,
                            im/qq, im/xmpp, im/msn, im/icq, im/gtalk, im/aim,
                            im/irc, im/yy, im/fetion, im/alibaba,
                            web/site, web/baidu, web/facebook, web/twitter,
                            web/googleplus, web/sinaweibo,
                            other
            recognize   dict(associative array), with recognized keys as
                        listed:
                            id/card, id/passport

                    note that for each associative array, with given key user
                    can specify an array of multiple values. Each value have
                    same limits in length: [1,256].

        All above item values are limited to a charset with:
            a-z A-Z 0-9 _@#/\.:=+
        """
       
        test_result = self._test_data(title, describe, **argv)
        if test_result == False: return False

        self._title, self._describe, self._contact, self._recognize =\
            test_result
        self._loaded = True

    def _test_data(self, title, describe, **argv):
        passed = (
            (self._filter_string(title) in xrange(5,31)) and
            (self._filter_string(describe) in xrange(0,141))
        )

        contact, recognize = {}, {}

        if argv.has_key('contact'):
            passed &= self._filter_dict(
                argv['contact'],
                self.get_contact_methods()
            )

        if argv.has_key('recognize'):
            passed &= self._filter_dict(
                argv['recognize'],
                self.get_recognize_methods()
            )
        if passed == True:
            return title, describe, contact, recognize
        else:
            return False

    def load_string(self, string):
        try:
            title = string['title']
            describe = string['describe']
            contact, recognize = {}, {}
            if string.has_key('contact'): contact = string['contact']
            if string.has_key('recognize'): contact = string['recognize']

            self.initialize(
                title,
                describe,
                contact=contact,
                recognize=recognize
            )

        except:
            raise RuntimeError('Failed to load given identity data.')

    def __str__(self):
        if not self._loaded:
            return ''
        else:
            ret = {
                'title': self._title,
                'describe': self._describe,
            }
            if self._contact: ret['contact'] = self._contact
            if self._recognize: ret['recognize'] = self._recognize
            return ret

    def get_id(self):
        if not self._loaded: return
        hasher = object_hasher('SHA-1')
        return hasher.hash(self.__str__()).encode('hex')

    def _filter_dict(self, dictobj, possible_keys):
        for each in dictobj:
            if not each in possible_keys:
                return False
            if type(dictobj[each]) == str:
                dictobj[each] = [dictobj[each],]
            elif type(dictobj[each]) != list:
                return False
            for item in dictobj[each]:
                if not self._filter_string(item) in xrange(1,257):
                    return False
        return True

    def _filter_string(self, string):
        if type(string) != str:
            return None
        string = string.lower().translate(
            None,
            'abcdefghijklmnopqrstuvwxyz0123456789_@#/\.:=+'
        )
        if string == '':
            return len(string)
        else:
            return None

    def get_contact_methods(self):
        return [i.strip() for i in """
            phone, mobile, fax,
            email, qq, xmpp, msn, icq, gtalk, aim, irc,
            web, addr 
        """.split(',')]

    def get_recognize_methods(self):
        return [i.strip() for i in """
            id/card, id/passport
        """.split(',')]

if __name__ == '__main__':
    import sys

    import json

    from _geheimnis_ import get_database, output_formator

    output = output_formator()

    try:
        user_identifier, db_access_key, operand = sys.argv[1:4]
        argument = ''
        if len(sys.argv) > 4:
            argument = ' '.join(sys.argv[4:])
    except Exception,e:
        output.error("Usage: python identity.py " +\
            "<USER_IDENTIFIER> <DB_ACCESS_KEY> <OPERAND> [ARGUMENTS]")
        exit()

#    try:
    db_access_key = db_access_key.decode('hex')
    database = get_database(user_identifier, db_access_key)
#    except Exception,e:
#        output.error('Cannot connect to database. Reason: %s' % e, 401)
#        exit()

    operand = operand.strip().lower()
    if operand not in ['list', 'add', 'delete', 'consult']:
        output.error('Unrecognized operand.', 405)
        exit()


    if operand == 'list':
        result = database.get('identities')
        output.result(
            json.dumps(
                result.keys()
            )
        )

    elif operand == 'consult':
        if argument == 'contact':
            output.result(
                json.dumps(
                    identity().get_contact_methods()
                )
            )
        elif argument == 'recognize':
            output.result(
                json.dumps(
                    identity().get_recognize_methods()
                )
            )
        else:
            output.error('Consult failed.', 400)

    elif operand == 'delete':
        database.remove('identities', argument)
        output.result('Deleted.')

    elif operand == 'add':
        output.result('Not yet implemented.', 501) # XXX WTF
