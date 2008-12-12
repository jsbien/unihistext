
import os, sys, unicodedata, codecs, signal
from functools import wraps
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

def _safe_op(op, collection, fallback):
    try:
        return op(collection)
    except ValueError:
        return fallback

def safe_max(collection, fallback = 0):
    return _safe_op(max, collection, fallback)

def safe_min(collection, fallback = int(2 ** 31 - 1)):
    return _safe_op(min, collection, fallback)

def make_main(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyboardInterrupt:
            sys.exit(128 + signal.SIGINT)
    return wrapper
