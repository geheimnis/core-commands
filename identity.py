#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Identity Management System
==========================

Synopsis
--------
python identity.py <USER_IDENTIFIER> <OPERAND> [ARGUMENTS]

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

from _geheimnis_ import get_database

class identity:

    def __init__(self, init_param=None):
        pass

    def create(self, title, describe, **argv):
        """Create a new identity.

        Recognized arguments are:
            title       size: [5, 30], a title of this new identity.
            describe    size: [0, 140], a brief description.
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
        """
        
        passed = (
            (self.filter_string(title) in xrange(5,31)) and
            (self.filter_string(describe) in xrange(0,141)
        )

        contact, recognize = {}, {}

        if argv.has_key('contact'):
            pass

        if argv.has_key('recognize'):
            pass

    def filter_string(self, string):
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

test = identity()
print test.get_contact_methods()
