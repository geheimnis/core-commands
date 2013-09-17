# -*- coding: utf-8 -*-

from Crypto.PublicKey import RSA


class Implementation:

    _obj = None
    _self_signature = None

    def __init__(self, load=''):
        pass

    def has_private_key(self):
        pass

    def can_encrypt(self):
        if self._obj == None:
            raise Exception('RSA can_encrypt - instance not initialized.')
        return self._obj.can_encrypt()

    def can_sign(self):
        if self._obj == None:
            raise Exception('RSA can_sign - instance not initialized.')
        return self._obj.can_sign()

    def generate(self, owner, **param):
        bits = int(param['bits'])
        if bits % 256 != 0 or bits / 256 < 4:
            raise Exception(
                'RSA generate - invalid bits(%s) specified.' % bits
            )

        self._obj = RSA.generate(bits)
        self._self_sign(owner)

    def encrypt(self):
        pass

    def decrypt(self):
        pass

    def sign(self, plaintext):
        pass

    def verify(self, plaintext):
        pass

    def _self_sign(self, owner):
        pass

    def _verify_self_sign(self):
        pass

    def get_private_key(self):
        pass

    def get_public_key(self):
        pass

    def get_fingerprint(self):
        pass

def self_test():
    # Generate RSA key-pair.
    new_key = Implementation()
    new_key.generate('Test Owner', bits=2048)


if __name__ == '__main__':
    self_test()
