#!/usr/bin/env python

__author__ = "Piotr Findeisen <piotr.findeisen@gmail.com>"

import sys, os, os.path, re
import unicodedata
from itertools import imap
from functools import partial
import codecs
from helpers import *

@make_main
def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] [[-n] NORM]")
    parser.add_option("-V", "--version", help="print version and exit", default=False, action="store_true")
    parser.add_option("-i", "--input", dest="input", help="read Unicode stream from FILE ('-' means stdin, this is the default)", metavar="FILE", default="-")
    parser.add_option("--encoding", help="set input/output streams binary encoding ('utf-8' is the default)", default='utf-8')
    parser.add_option("-n", "--normalization", help="use specific normalization as defined in Unicode Standard\nPossible values are NFC (default), NFKC, NFD, and NFKD",
            metavar="NORM", default=None)
    parser.add_option("-N", "--no-normalization", help="skip Unicode Standard normalization phase; " +
            "option --normalization is used to parse corrections defined in --post-* files",
            default=False, action="store_true")
    parser.add_option("--post-compose", help=
            "for each character listed in FILE replace its NFD (for NFC, NFD normalizations) or NFKD (for NFKD, NFKC normalizations) " +
            "form with itself in output; all replacements (also those from --post-decompose) are applied from left to right \"first match first apply\";" +
            "when reading FILE, sequences from '#' to '\\n' and ASCII blank characters are removed, empty lines are ignored; " +
            "what remains should by 1 character in line, UTF-8 encoded")
    parser.add_option("--post-decompose", help="if normalization if NFC or NFKC, each character listed in FILE is replace on output with its NFD form; " +
            "FILE format is the same as for --post-compose")
    parser.add_option("-v", "--verbose", help="be verbose", action="store_true", default=False)
    
    run(*parser.parse_args())
    parser.destroy()

def get_line_meat(line):
    return line.partition('#')[0].strip()

def _make_post_rewritings(options, fixups, file, norm, encoding = 'utf-8'):
    for lineno, line in enumerate(unicode_xreadlines(open(file, 'rb'), encoding=encoding)):
        line = get_line_meat(line)
        if not line: continue
        if len(line) > 1: die("more than one Unicode character in %r line %d: %r", file, lineno + 1, line)
        if ord(line) < 128: die("%r line %d: illegal character %r -- defining rewriting of ASCII (7-bit) characters is not allowed", file, lineno + 1, line.encode('ascii'))
        fixups[line] = unicodedata.normalize(norm, line)
        if options.verbose:
            print >> sys.stderr, "Every '%s' (%r) will be changed back into '%s' (%r)" % (line, line, fixups[line], fixups[line])

# handle options.post_decompose
def make_redecompose_compositions(options, fixups):
    if not options.post_decompose or options.normalization not in ('NFC', 'NFKC'): return
    return _make_post_rewritings(options, fixups, options.post_decompose, 'NFD')

# handle options.post_compose
def make_recompose_decompositions(options, fixups):
    if not options.post_compose: return
    return _make_post_rewritings(options, fixups, options.post_compose, { 'NFC': 'NFD', 'NFKC': 'NFKD' }.get(options.normalization, options.normalization))

def pairs(collection):
    collection = iter(collection)
    while True:
        first = collection.next()
        try: second = collection.next()
        except StopIteration:
            raise ValueError, "collection doesn't have even number of elements"
        yield first, second
            

def compile_fixups(options, fixups):
    if not fixups: return identity
    r = re.compile("(" + "|".join(fixups.iterkeys()) + ")")
    def fixer(n):
        s = r.split(n)
        if len(s) == 1: return s[0]
        n = s[0]
        for sep, norm in pairs(s[1:]):
            n += fixups[sep] + norm
        return n
    return fixer

def run(options, args):
    if options.version:
        return print_version()
    if args:
        options.normalization = args[0]
        args = args[1:]
    if not options.normalization: options.normalization = 'NFC'
    else:
        options.normalization = options.normalization.upper()
        if options.normalization not in ('NFC', 'NFKC', 'NFD', 'NFKD'):
            die("unknown normalization %r", options.normalization)

    if not options.no_normalization: normalization = partial(unicodedata.normalize, options.normalization)
    else: normalization = identity

    fixups = {}
    make_redecompose_compositions(options, fixups)
    make_recompose_decompositions(options, fixups)
    apply_fixups = compile_fixups(options, fixups)
    del fixups

    for l in open_input(options):
        n = normalization(l)
        n = apply_fixups(n)
        sys.stdout.write(n.encode(options.encoding))

if __name__ == "__main__":
    main()
