import sys
import os
import time
import datetime

dt = datetime.datetime.now()

print "***** Arrival of Core Command Region ***"
print "SYS.ARGV:"
print repr(sys.argv), '\n'
print "MY PATH:"
print os.path.realpath(os.path.dirname(sys.argv[0])), "\n"
print "NOW: %.6f" % (time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0)
print "*" * 40
