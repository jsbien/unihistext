
import os, sys, unicodedata, codecs
import version

def print_version():
    print os.path.basename(sys.argv[0]) + " version " + version.version
    print "Supported Unicode version: " + unicodedata.unidata_version

def unicode_file(file, encoding = 'utf-8', errors = 'strict'):
    # copied from codecs.open
    info = codecs.lookup(encoding)
    srw = codecs.StreamReaderWriter(file, info.streamreader, info.streamwriter, errors)
    # Add attributes to simplify introspection
    srw.encoding = encoding
    return srw

def unicode_xreadlines(input, *args, **kwargs):
    return iter(unicode_file(input, *args, **kwargs))

def open_input(options, **kwargs):
    input = sys.stdin if options.input == "-" else open(options.input, 'rb')
    encoding = kwargs.get('encoding', getattr(options, 'encoding', None))
    if encoding is not None:
        input = unicode_file(input, encoding=encoding, **kwargs)
    return input

def die(fmt, *args):
    print >> sys.stderr, fmt % args
    sys.exit(1)
