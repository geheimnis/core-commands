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

import msgpack

from hash import hash_generator
from cryptoalgo.symmetric import serpent, twofish, rijndael, xxtea

class xipher(object):

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
        keylen = 0
        for x in self.cipherlist:
            keylen += x[1]

        if len(key) < keylen:
            raise Exception("Key too short. At least %d bytes required." % keylen)
        
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
        derivedkey = key[:]
        for i in xrange(len(self.cipherlist)):
            keyring = derivedkey[:]
            for x in shifting_list:
                self.encrypt_chain.append((x[0],keyring[0:x[1]]))
                keyring = keyring[x[1]:]
            derivedkey = _derivekey.derive_key(derivedkey)

            shifting_first = shifting_list[0]
            shifting_list = shifting_list[1:]
            shifting_list.append(shifting_first)

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
            result[i] = chr(ord(stream[i]) ^ ord(data[i]))
        return ''.join(result)

    def keystream(self,times,iv):
        #print "Generating keystream of %d times basing on [%s]." % (times,iv.encode('hex'))
        ret = ''
        block = ''
        for i in xrange(times):
            block += "%8s%8s" % (iv,hex(i)[2:])

        ciblk = self._encrypt_block(block)

        #print "KeyStream:" + ciblk.encode('hex')
        return ciblk

    def encrypt(self, data):    # Use CFB
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

        keystream = self.keystream(times,iv)
        #print "KeyStream:" + keystream.encode('hex')
        
#        teststart = time.time()
        result = rand + str(iv0) + str(self._xor_stream(keystream,data))
#        testend = time.time()

#        print "Xor Time Cost: %f seconds." % (testend - teststart)
        
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

        keystream = self.keystream(times,iv)
                
        result = self._xor_stream(keystream,data)
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
    x = xipher('a' * 512)
    print x.encrypt('hallo')