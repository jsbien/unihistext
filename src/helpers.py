
import os, sys, unicodedata, version

def print_version():
    print os.path.basename(sys.argv[0]) + " version " + version.version
    print "Supported Unicode version: " + unicodedata.unidata_version

def die(fmt, *args):
    print >> sys.stderr, fmt % args
    sys.exit(1)
