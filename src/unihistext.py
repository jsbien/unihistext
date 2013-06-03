
__author__ = "Piotr Findeisen <piotr.findeisen@gmail.com>"

import sys, os, os.path
import unicodedata
from itertools import imap
import codecs
import operator

from helpers import *
import unicode_blocks

@make_main
def main():

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input", help="read Unicode stream from FILE ('-' means stdin, this is the default)", metavar="FILE", default="-")
    parser.add_option("-f", "--encoding", help="set input stream binary encoding ('utf-8' is the default)", default='utf-8')
    parser.add_option("-l", "--list-encodings", help="list available encodings and exit", default=False, action="store_true")
    parser.add_option("-V", "--version", help="print version and exit", default=False, action="store_true")
    parser.add_option("-c", "--combining", help="recognize combining character sequences", default=False, action="store_true")
    parser.add_option("-n", "--names", help="print names of Unicode characters or sequences", default=False, action="store_true")
    parser.add_option("-N", "--block-names",
        help="print names of blocks for Unicode characters",
        default=False, action="store_true")
    parser.add_option("-S", "--sequence-names-file", help="use file in format of NamedSequences.txt from Unicode instead of system default",
            default="/usr/share/unicode/NamedSequences.txt", metavar="FILE")
    parser.add_option("-C", "--only-combining", help="print only combining character sequences", default=False, action="store_true")
    parser.add_option("-b", "--blocks", help="make statistics of Unicode blocks instead of separate code points", default=False, action="store_true")
    parser.add_option("--blocks-definitions", help="read blocks definitions from FILE", metavar="FILE",
            default="/usr/share/unicode/Blocks.txt")
    parser.add_option("-B", "--filter-block", help="make statistics only for caracters in BLOCK_NAME as reported by --blocks; " + \
            "block names are case insensitive (may be repeated)", metavar="BLOCK_NAME", action="append")
    parser.add_option("-s", "--sort",
        help="sort statistics by METHOD which is 'block', 'code'" +
            " or 'frequency' (default)",
        choices=('block', 'code', 'frequency'), metavar="METHOD",
        default='frequency')

    run(*parser.parse_args())
    parser.destroy()

def list_encodings():
    encs = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp1006', 'cp1026', 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257',
            'cp1258', 'cp424', 'cp437', 'cp500', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864',
            'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'euc_jis_2004', 'euc_jisx0213', 'euc_jp', 'euc_kr', 'gb18030', 'gb2312',
            'gbk', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'iso8859_10',
            'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9',
            'johab', 'koi8_r', 'koi8_u', 'latin_1', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154',
            'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8']
    maxlen = max(len(e) + 2 for e in encs)
    termcols = 80
    cols = termcols / maxlen
    for row in range((len(encs) - 1) / cols + 1):
        for col in range(cols):
            pos = row * cols + col
            if pos < len(encs):
                sys.stdout.write(encs[pos].ljust(maxlen))
        sys.stdout.write("\n")
    print
    print "Any encoding supported by Python's codecs module is supported."
    print "For a complete list of supported encodings"
    print "visit http://www.google.com/search?q=python+standard+encodings."
    print

def is_combining(unichr, more_combinings = (unicodedata.lookup('zero width joiner'), unicodedata.lookup('zero width non-joiner'))):
    return unichr in more_combinings or unicodedata.combining(unichr) != 0

def glue_combinings(unichr, line, i):
    while i != len(line) and is_combining(line[i]):
        unichr += line[i]
        i += 1
    return unichr, line, i

def make_block_abstracter(options):
    unicode_blocks.initialize(options.blocks_definitions, options)
    return lambda unichr, line, i: (unicode_blocks.block(unichr), line, i)

def make_block_filter(options):
    unicode_blocks.initialize(options.blocks_definitions, options)
    names = [n.lower().strip() for n in options.filter_block]
    return lambda unichr, line, i: (unicode_blocks.block(unichr).name.lower().strip() in names)

def make_stats(input, options, args):
    if options.combining and options.blocks:
        die("you cannot use --combining and --blocks together")
    if options.combining:
        glue_combinings_ = glue_combinings
    else:
        glue_combinings_ = lambda *args: args

    if options.blocks: abstract_block = make_block_abstracter(options)
    else: abstract_block = lambda *args: args

    def combine_filters(filt1, filt2):
        return lambda *args: filt1(*args) and filt2(*args)

    filter = lambda *args: True
    if options.filter_block: filter = combine_filters(make_block_filter(options), filter)

    stats = {}
    for line in input:

        i = 0
        while i != len(line):
            off = i
            unichr = line[i]
            i += 1
            if not filter(unichr, line, i): continue
            unichr, line, i = glue_combinings_(unichr, line, i)
            unichr, line, i = abstract_block(unichr, line, i)
            stats[unichr] = stats.get(unichr, 0) + 1
    return stats

# output formatting
class Formatter(object):
    @staticmethod
    def fmt(d, totals):
        return ""
    @staticmethod
    def stat(d, totals):
        pass
    @staticmethod
    def prep(d, totals):
        pass
    @staticmethod
    def filter(d, totals):
        return True

class StatFmt(Formatter):
    @staticmethod
    def stat(stats, totals):
        totals['total_count'] = sum(d['count'] for d in stats)
    @staticmethod
    def fmt(d, totals):
        return "%8.3f %8d" % (d['count'] * 100.0 / totals['total_count'], d['count'])

class HexFmt(Formatter):
    @staticmethod
    def fmt(d, totals):
        return "        %*s" % (totals['max_hexs_len'], d['hexs'])
    @staticmethod
    def prep(d, totals):
        d['hexs'] = " ".join([ "0x%.6X" % ord(unichr) for unichr in d['unistr'] ]) # convert unistr to HEXes
    @staticmethod
    def stat(stats, totals):
        totals['max_hexs_len'] = safe_max(len(d['hexs']) for d in stats)

class UnistrFmt(Formatter):
    @staticmethod
    def fmt(d, totals):
        f = "  \t%s\t"
        for unichr in d['unistr']:
            if unicodedata.category(unichr) in ('Cc', 'Cf', 'Zl', 'Zp'):
                return f % ""
        return f % d['unistr']

class BlockNameFmt(Formatter):
    def __init__(self):
        assert unicode_blocks.isinitialized()

    def fmt(self, d, totals):
        return " %s " % d['unistr'].name

class NameFmt(Formatter):
    mapping = {}
    def __init__(self, named_sequences_file = None):
        if named_sequences_file is not None:
            self.mapping = {}
            for line in definition_file_xreadlines(named_sequences_file):
                try:
                    name, codes = line.split(";")
                    unistr = u"".join(unichr(int(codepoint, 16)) for codepoint in codes.split())
                    self.mapping[unistr] = name
                except Exception:
                    import traceback; traceback.print_exc()

    def _name(self, unichr):
        try:
            return unicodedata.name(unichr)
        except ValueError:
            return ""

    def prep(self, d, totals):
        if d['unistr'] in self.mapping:
            d['name'] = self.mapping[d['unistr']]
            return
        d['name'] = ", ".join(filter(None, map(self._name, d['unistr'])))
        if self.options.combining and is_combining(d['unistr'][0]) and is_combining(d['unistr']):
            d['name'] = "<no base> " + d['name']
    @staticmethod
    def stat(stats, totals):
        totals['max_name_len'] = safe_max(len(d['name']) for d in stats)
    @staticmethod
    def fmt(d, totals):
        return "%-*s" % (totals['max_name_len'] + 3, d['name'])

class JustBlockNameFmt(Formatter):
    def __init__(self, options):
        Formatter.__init__(self)
        unicode_blocks.initialize(options.blocks_definitions, options)
    def prep(self, d, totals):
        d['block_name'] = '';
        if len(d['unistr']) == 1:
            d['block_name'] = unicode_blocks.block(d['unistr']).name

    def stat(self, stats, totals):
        totals['max_block_name_len'] = safe_max(len(d['block_name']) for d in stats)

    def fmt(self, d, totals):
        return "%-*s" % (totals['max_block_name_len'] + 3, d['block_name'])

class OnlyCombiningFilter(Formatter):
    def filter(self, d, totals):
        for unichr in d['unistr']:
            if is_combining(unichr): return True
        return False

def print_hist(input, options, args):
    stats = make_stats(input, options, args)
    stats = list(stats.iteritems())
    if not stats:
        print >> sys.stderr, "Empty input or all Unicode code points filtered out."
        return
    if options.sort == 'frequency':
        stats.sort(key=operator.itemgetter(1), reverse=True) # sort by occurrences
    elif options.sort == 'code':
        if options.blocks:
            die("you cannot use --blocks and --sort 'code' together")
        stats.sort(key=operator.itemgetter(0), reverse=False)
    elif options.sort == 'block':
        if options.blocks:
            assert unicode_blocks.isinitialized()
            stats.sort(key=lambda t: t[0].id, reverse=False)
        elif options.combining:
            die("you cannot use --combining and --sort 'block' together")
        else:
            unicode_blocks.initialize(options.blocks_definitions, options)
            stats.sort(key=lambda t: unicode_blocks.block(t[0]).id, reverse=False)
    else:
        die("sorting method %r is not implemented" % options.sort)
    totals = {}
    stats = [ {'unistr': unistr, 'count': count } for (unistr, count) in stats ] # convert each entry to dict

    fmts = [StatFmt()]
    if not options.blocks:
        fmts.extend([HexFmt(), UnistrFmt()])
    else:
        fmts.append(BlockNameFmt())

    if options.names:
        if options.blocks:
            die("you cannot use --names and --blocks together")
        fmts.append(NameFmt(options.sequence_names_file))
    if options.block_names:
        if options.blocks:
            die("you cannot use --block-names and --blocks together")
        fmts.append(JustBlockNameFmt(options))

    if options.only_combining:
        if options.blocks: die("you cannot use --only-combining and --blocks together")
        fmts.append(OnlyCombiningFilter())

    for fmt in fmts:
        fmt.options = options
        fmt.args = args

    # apply filtering
    for fmt in fmts:
        stats = ( d for d in stats if fmt.filter(d, totals) )

    stats = list(stats)
    for fmt in fmts:
        for d in stats:
            fmt.prep(d, totals)
        fmt.stat(stats, totals)

    for d in stats:
        print "".join(fmt.fmt(d, totals) for fmt in fmts).rstrip()

def run(options, args):
    if options.version:
        return print_version()
    if options.list_encodings:
        return list_encodings()
    return print_hist(open_input(options), options, args)

if __name__ == "__main__":
    main()
