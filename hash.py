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

class hash_function:

    _options = {
        'algorithm': 'MD5',
        'output': 'HEX',
        'HMAC': False,
    }

    def __init__(self):
        self._update()

    def _update(self):
        """Update the hash generator within this class by options."""
        pass

    def option(self, *argv):
        """Get or set a option.

        Usage:
         .option()  # get a list of all options and their values.
         .option('algorithm')  # gets what algorithm is being used.
         .option('algorithm','SHA-1')  # set to use SHA-1 as algorithm.
        """
        if len(argv) == 0:
            return self._options
        else:
            option_key = argv[0]
            option_values = argv[1:]
            if not option_key in self._options.keys():
                raise RuntimeError('Unrecognized option name.')

        if len(option_values) == 0:
            return self._options[option_key]
        else:
            self._options[option_key] = option_values[0]
            self._update()
            return self

    def get_hash(self, text):
        """Generate a hash."""


if __name__ == '__main__':
    pass
