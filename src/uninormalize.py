#!/usr/bin/env python

__author__ = "Piotr Findeisen <piotr.findeisen@gmail.com>"

import sys, os, os.path
import unicodedata
from itertools import imap
import codecs
from helpers import print_version

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-v", "--version", help="print version and exit", default=False, action="store_true")
    
    run(*parser.parse_args())

def run(options, args):
    if options.version:
        return print_version()
    pass

if __name__ == "__main__":
    main()
