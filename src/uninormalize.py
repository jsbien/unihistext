#!/usr/bin/env python

__author__ = "Piotr Findeisen <piotr.findeisen@gmail.com>"

import sys, os, os.path
import unicodedata
from itertools import imap
import codecs
from helpers import *

def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] [[-n] NORM]")
    parser.add_option("-V", "--version", help="print version and exit", default=False, action="store_true")
    parser.add_option("-i", "--input", dest="input", help="read Unicode stream from FILE ('-' means stdin, this is the default)", metavar="FILE", default="-")
    parser.add_option("--encoding", help="set input/output streams binary encoding ('utf-8' is the default)", default='utf-8')
    parser.add_option("-n", "--normalization", help="use specific normalization as defined in Unicode Standard\nPossible values are NFC (default), NFKC, NFD, and NFKD",
            metavar="NORM")
    
    run(*parser.parse_args())
    parser.destroy()

def run(options, args):
    if options.version:
        return print_version()
    if args:
        options.normalization = args[0]
        args = args[1:]
    if not options.normalization:
        options.normalization = 'NFC'
    options.normalization = options.normalization.upper()
    if options.normalization not in ('NFC', 'NFKC', 'NFD', 'NFKD'):
        die("%s: unknown normalization %r", os.path.basename(sys.argv[0]), options.normalization)

    for l in open_input(options):
        print unicodedata.normalize(options.normalization, l).encode(options.encoding)

if __name__ == "__main__":
    main()
