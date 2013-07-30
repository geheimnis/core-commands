#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Encryption/Decryption with Codebook
===================================

Description
-----------
This program encrypts or decrypts a string, using a codebook. The codebook
is an entry in database, containing a long confidential data, and belongs to
certain identities. When encrypting, program randomly picks a few bytes from
the codebook, then assemble them as a encrypt key. When decrypting, hints
in the beginning of ciphertext, which records how to reassemble the key, is
read. The suggestion is, do not use a codebook for unlimited period. While it
is recommended to use each key only once, we here do not take this plan, as
good symmetric ciphers can also secure the key from being revealed, and
implementing this plan makes the program more complex.

On the cipher
-------------
"""
import random
import zlib

import msgpack

from hash import hash_generator
from cryptoalgo.symmetric import serpent, twofish, rijndael, xxtea, blowfish

class xipher:

    cipherlist = [
        [serpent.Serpent, serpent.key_size],
        [twofish.Twofish, twofish.key_size],
        [rijndael.get_class(), rijndael.key_size],
        [xxtea.XXTEA, xxtea.key_size],
    ]
    blocksize  = 16
    ivsize = 8

    encrypt_chain = []

    _whirlpool_hasher = None
    _sha512_hasher = None

    def __init__(self, key):
        """Initialize this class using a 'key'."""
        self._whirlpool_hasher = hash_generator().option({
            'output_format': 'raw',
            'algorithm': 'WHIRLPOOL',
            'HMAC': False,
        })
        self._sha512_hasher = hash_generator().option({
            'output_format': 'raw',
            'algorithm': 'SHA-512',
            'HMAC': False,
        })

        shifting_list = self.cipherlist[:]
        self.encrypt_chain = []
        derivedkey = self._derive_key(key)
        key = None
        del key
        for i in xrange(len(self.cipherlist)):
            keyring = derivedkey[:]
            for x in shifting_list:
                self.encrypt_chain.append((x[0],keyring[0:x[1]]))
                keyring = keyring[x[1]:]
            derivedkey = self._derive_key(derivedkey)

            shifting_first = shifting_list[0]
            shifting_list = shifting_list[1:]
            shifting_list.append(shifting_first)
        derivedkey = None
        del derivedkey

    def _derive_key(self, oldkey):
        key_whirlpool = self._whirlpool_hasher.digest(oldkey)
        key_sha512 = self._sha512_hasher.digest(oldkey)
        ret = ['  '] * 64
        for i in xrange(64):
            ret[i] = key_whirlpool[i] + key_sha512[i]
        return ''.join(ret)

    def _encrypt_block(self,data):
        length = len(self.encrypt_chain)
        for i in xrange(length):
            tool = self.encrypt_chain[i]
            data = tool[0](tool[1]).encrypt(data)
        return data

    def _xor_stream(self,stream,data):
        datalen = len(data)
        if len(stream) < datalen:
            raise Exception("Length of bitstream is not sufficient.")
        result = [' '] * datalen
        for i in xrange(datalen):
            result[i] = stream[i] ^ data[i] #chr(ord(stream[i]) ^ ord(data[i]))
        result = [i for i in result]
        return result

    def keystream(self,times,iv):
        """Generate a counter stream with initial vector.
        
        'times' is how much the counter repeats.
        'iv' is initial vector."""
        
        ret = ''
        block = ['aaaabbbbccccdddd'] * times
        for i in xrange(times):
            block[i] = "%8s%8s" % (iv,hex(i)[2:])
        block = ''.join(block)

        ciblk = self._encrypt_block(block)
        ciblk = [ord(i) for i in ciblk]
        return ciblk

    def encrypt(self, data): 
        """Encrypt data in CFB mode."""
        rand = ''
        for i in xrange(self.blocksize / 4 * 3):
            rand += chr(random.randint(0,255))
        rand = rand.encode('base64')[0:self.blocksize]

        iv = hex(abs(int(zlib.crc32(rand + data))))[2:2+self.ivsize]
        if len(iv) < self.ivsize:
            iv += (self.ivsize - len(iv)) * '*'
        
        iv0 = iv[:]
        
        # generate CFB keystream
        datalen = len(data)

        times = datalen / self.blocksize
        if datalen % self.blocksize != 0:
            times += 1

        keystream = self.keystream(times, iv)
        data = [ord(i) for i in data]

        xor_result = [chr(i) for i in self._xor_stream(keystream, data)]
        result = rand + str(iv0) + ''.join(xor_result)
        
        return result

    def decrypt(self,data):
        rand = data[0:self.blocksize]
        data = data[self.blocksize:]
        # generate CFB iv
        iv = data[0:self.ivsize].strip()
        
        data = data[self.ivsize:]
        # generate CFB keystream
        datalen = len(data)

        times = datalen / self.blocksize
        if datalen % self.blocksize != 0:
            times += 1

        keystream = self.keystream(times, iv)
        data = [ord(i) for i in data]
                
        xor_result = self._xor_stream(keystream,data)
        result = ''.join([chr(i) for i in xor_result])
        digest = hex(abs(int(zlib.crc32(rand + result))))[2:10]
        #if len(digest) < self.ivsize:
        #    digest += (self.ivsize - len(iv)) * '*'
         

        if digest == iv[0:len(digest)]:
            #print 'verified.'
            return result
        else:
            raise Exception("Cannot decrypt. Data corrupted or incorrect key.")

    def get_version(self):
        return 1

if __name__ == '__main__':

    import time


    x = xipher('a' * 512)
    y = xipher('a' * 512)
    src = 'hallo' * 100
    times = 1

    begin = time.time()
    for i in xrange(times): 
        ctext = x.encrypt(src)
        ptext = y.decrypt(ctext)
    end = time.time()

    print len(src) * times / (end-begin), 'bytes per second.'
        
