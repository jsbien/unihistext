
from bisect import bisect_left
from helpers import *


class BlockName(object):
    def __init__(self, name):
        self.name = name

_initialized = False
fallback = BlockName("No_Block")
block_names = []

def initialize(path, options):
    global _initialized
    if _initialized: return
    for line in definition_file_xreadlines(path):
        try:
            range, colon, name = line.partition(';')
            assert colon == ';'
            lo, _, hi = range.partition('..')
            assert hi is not None
            lo, hi = int(lo, 16), int(hi, 16)
            block_names.append((lo, hi, BlockName(name.strip())))

        except Exception:
            import traceback; traceback.print_exc()
    _initialized = True

def isinitialized():
    return _initialized

def block(unichr):
    assert len(unichr) == 1
    if not block_names: return fallback
    cp = ord(unichr)
    j = bisect_left(block_names, (cp, None, None))
    if j > 0: j -= 1
    assert block_names[j][0] <= cp
    while j < len(block_names) and block_names[j][1] < cp: j += 1
    if j >= len(block_names): return fallback
    return block_names[j][2]
