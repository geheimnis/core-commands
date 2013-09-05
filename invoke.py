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

<OPERAND> may be either 'run' or 'query'.

When <OPERAND> is 'query', <ARGUMENTS> is a string of Result-ID.
When <OPERAND> is 'run', <ARGUMENTS> are instructions of running an actual
command.

Arguments <USER-IDENTIFIER>, <DATABASE-ACCESS-KEY>, [ARGUMENTS] are encoded
in HEX.
"""

if __name__ == '__main__':
    import sys
    import os

    from _geheimnis_ import get_database

    if len(sys.argv) < 4:
        print "Usage: python invoke.py <USER-IDENTIFIER>" + \
            "<DATABASE-ACCESS-KEY> <OPERAND> [ARGUMENTS]"
        exit()

    
