#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generic Purpose Hashing Program
===============================

Description
-----------
This program takes a string as input, and outputs hashed result. Input string
must be base64-encoded, but they are decoded before hashed. The output format
can be set by arguments, by default it is HEX. HMAC can also be calculated, by
specifying commandline arguments.

"""

class hash_generator:


    __trans_5C = """\\]^_XYZ[TUVWPQRSLMNOHIJKDEFG@ABC|}~\x7fxyz{tuvwpqrslmnohijkdefg`abc\x1c\x1d\x1e\x1f\x18\x19\x1a\x1b\x14\x15\x16\x17\x10\x11\x12\x13\x0c\r\x0e\x0f\x08\t\n\x0b\x04\x05\x06\x07\x00\x01\x02\x03<=>?89:;45670123,-./()*+$%&\' !"#\xdc\xdd\xde\xdf\xd8\xd9\xda\xdb\xd4\xd5\xd6\xd7\xd0\xd1\xd2\xd3\xcc\xcd\xce\xcf\xc8\xc9\xca\xcb\xc4\xc5\xc6\xc7\xc0\xc1\xc2\xc3\xfc\xfd\xfe\xff\xf8\xf9\xfa\xfb\xf4\xf5\xf6\xf7\xf0\xf1\xf2\xf3\xec\xed\xee\xef\xe8\xe9\xea\xeb\xe4\xe5\xe6\xe7\xe0\xe1\xe2\xe3\x9c\x9d\x9e\x9f\x98\x99\x9a\x9b\x94\x95\x96\x97\x90\x91\x92\x93\x8c\x8d\x8e\x8f\x88\x89\x8a\x8b\x84\x85\x86\x87\x80\x81\x82\x83\xbc\xbd\xbe\xbf\xb8\xb9\xba\xbb\xb4\xb5\xb6\xb7\xb0\xb1\xb2\xb3\xac\xad\xae\xaf\xa8\xa9\xaa\xab\xa4\xa5\xa6\xa7\xa0\xa1\xa2\xa3"""
    __trans_36 = """67452301>?<=:;89&\'$%"# !./,-*+()\x16\x17\x14\x15\x12\x13\x10\x11\x1e\x1f\x1c\x1d\x1a\x1b\x18\x19\x06\x07\x04\x05\x02\x03\x00\x01\x0e\x0f\x0c\r\n\x0b\x08\tvwturspq~\x7f|}z{xyfgdebc`anolmjkhiVWTURSPQ^_\\]Z[XYFGDEBC@ANOLMJKHI\xb6\xb7\xb4\xb5\xb2\xb3\xb0\xb1\xbe\xbf\xbc\xbd\xba\xbb\xb8\xb9\xa6\xa7\xa4\xa5\xa2\xa3\xa0\xa1\xae\xaf\xac\xad\xaa\xab\xa8\xa9\x96\x97\x94\x95\x92\x93\x90\x91\x9e\x9f\x9c\x9d\x9a\x9b\x98\x99\x86\x87\x84\x85\x82\x83\x80\x81\x8e\x8f\x8c\x8d\x8a\x8b\x88\x89\xf6\xf7\xf4\xf5\xf2\xf3\xf0\xf1\xfe\xff\xfc\xfd\xfa\xfb\xf8\xf9\xe6\xe7\xe4\xe5\xe2\xe3\xe0\xe1\xee\xef\xec\xed\xea\xeb\xe8\xe9\xd6\xd7\xd4\xd5\xd2\xd3\xd0\xd1\xde\xdf\xdc\xdd\xda\xdb\xd8\xd9\xc6\xc7\xc4\xc5\xc2\xc3\xc0\xc1\xce\xcf\xcc\xcd\xca\xcb\xc8\xc9"""

    _options = {
        'algorithm': 'MD5',
        'output_format': 'HEX',
        'HMAC': False,
    }

    _algorithms = {}

    _hash_module = None

    _choosen_algorithm = None

    _hmac_package = []

    def __init__(self):

        # Load hash functions
        self._hash_module = __import__('cryptoalgo.hash', fromlist='*')
        for each in self._hash_module.__all__:
            new_hash_class = getattr(self._hash_module, each).hash_class()
            self._algorithms[new_hash_class.get_name()] = [
                new_hash_class.get_block_size(),
                new_hash_class,
            ]

        self._update()

    def _output(self, binary_digest):
        output_format = self._options['output_format'].upper()
        if output_format == 'HEX': return binary_digest.encode('hex')
        if output_format == 'BASE64': return binary_digest.encode('base64')
        return binary_digest

    def _update(self):
        """Update the hash generator within this class by options."""

        # Choose the algorithm
        if not self._options['algorithm'] in self._algorithms.keys():
            raise RuntimeError('Unrecognized hash method.')
        choice = self._algorithms[self._options['algorithm']]
        self._choosen_algorithm = choice[1]
        blocksize = choice[0] / 8

        # Pre-calculate some values for HMAC
        if type(self._options['HMAC']) == str:
            hmac_key = self._options['HMAC']
            if len(hmac_key) > blocksize:
                hmac_key = self._choosen_algorithm.hash(hmac_key)
            else:
                hmac_key += chr(0) * (blocksize - len(hmac_key))
            o_key_pad = hmac_key.translate(self.__trans_5C)
            i_key_pad = hmac_key.translate(self.__trans_36)
            self._hmac_package = (o_key_pad, i_key_pad)
        else:
            self._hmac_package = False                

    def option(self, *argv):
        """Get or set a option.

        Usage:
         .option()             # get a list of all options and their values.
         .option('algorithm')  # gets what algorithm is being used.
         .option(
            'algorithm',
            'SHA-1'
         )                     # set to use SHA-1 as algorithm.
         .option({
            'algorithm': 'SHA-1',
            'output_format': 'HEX',
          })                   # Batch set a number of options.
        """
        if len(argv) == 0:
            return self._options
        else:
            leading_arg = argv[0]
            following_arg = argv[1:]
            if type(leading_arg) == dict:
                for each in leading_arg:
                    self.option(each, leading_arg[each])
                return self
            elif not leading_arg in self._options.keys():
                raise RuntimeError('Unrecognized option name.')

        if len(following_arg) == 0:
            return self._options[leading_arg]
        else:
            self._options[leading_arg] = following_arg[0]
            self._update()
            return self

    def get_hash(self, text):
        """Generate a hash."""
        raw_digest = self._choosen_algorithm.hash(text)
        return self._output(raw_digest)

    def get_hmac(self, text):
        """Generate a HMAC using given key.
        
        The key is preset by 'option' function.
        """
        if self._hmac_package == False:
            raise RuntimeError('HMAC key not set.')

        raw_digest = self._choosen_algorithm.hash(
            self._hmac_package[0] +
            self._choosen_algorithm.hash(
                self._hmac_package[1] +
                text
            )
        )
        return self._output(raw_digest)


if __name__ == '__main__':
    x = hash_generator()
    print x.option({
        'output_format': 'hex',
        'HMAC': 'key',
        'algorithm': 'MD5'
    }).get_hmac('The quick brown fox jumps over the lazy dog') 
