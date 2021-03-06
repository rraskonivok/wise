#!/usr/bin/env python

from datetime import datetime
import sys

# Read the ctags file produced by pure --ctags file

fn = []
symbols = []

for arg in sys.argv[1:]:
    fn.append(arg)

print '# Autogenerated by Wise annotation utility on', datetime.now()

print '''
try:
    from wise.worksheet.pure_wrap import use, PureSymbol
except ImportError:
    raise Exception('Could not load Cython Pure module, perhaps it needs to be built?')
'''

for fnx in fn:
    print "use('base','%s')" % fnx.split('.')[0]

for fnx in fn:
    fp = open('tags')
    for line in fp:
        if fnx in line:
            sym = line.split()[0]
            # Ignore private symbols
            if sym[0] != '_':
                symbols.append(line.split()[0])

    print '#', fnx
    for usym in set(symbols):
        print "%s = PureSymbol('%s')" % (usym,usym)
    symbols = []
    print '\n'
