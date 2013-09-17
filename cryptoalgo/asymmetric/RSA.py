# -*- coding: utf-8 -*-

"""
A textbook-style RSA implementation
===================================
This RSA implementation is mostly a wrapper of library pyCrypto, but modifying
interfaces so as all public key algorithms can use the same operational
sequence.
The implementation is as nature as possible. 
"""

from Crypto.PublicKey import RSA


class Implementation:

    _obj = None
    _self_signature = None

    def __init__(self, load=''):
        pass

    def has_private_key(self):
        self._check_initialized()
        return self._obj.has_private()

    def can_encrypt(self):
        self._check_initialized()
        return self._obj.can_encrypt()

    def can_sign(self):
        self._check_initialized()
        return self._obj.can_sign()

    def generate(self, **param):
        bits = int(param['bits'])
        if bits % 256 != 0 or bits / 256 < 4:
            raise Exception(
                'RSA generate - invalid bits(%s) specified.' % bits
            )

        self._obj = RSA.generate(bits)

    def encrypt(self):
        self._check_initialized()
         

    def decrypt(self):
        self._check_initialized()
        pass

    def sign(self, plaintext):
        self._check_initialized()
        pass

    def verify(self, plaintext):
        self._check_initialized()
        pass

    def get_private_key(self):
        self._check_initialized()
        pass

    def get_public_key(self):
        self._check_initialized()
        pass

    def get_fingerprint(self):
        self._check_initialized()
        pass

    def _check_initialized(self):
        if self._obj == None:
            raise Exception('RSA instance not initialized.')
        

def self_test():
    # Generate RSA key-pair.
    new_key = Implementation()
    new_key.generate(bits=1024)


if __name__ == '__main__':
    self_test()
