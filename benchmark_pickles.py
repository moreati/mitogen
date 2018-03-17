#!/usr/bin/env python

import os
try:
    import cPickle as pickle
except NameError:
    import pickle
import sys

import perf

sys.path.append(os.path.abspath('../'))
import cerealizer
import chopsticks.pencode
import safepickle

#sys.path.append('../Gnosis_Utils-1.2.2')
#import gnosis.xml.pickle

def setup():
    return [[
        1000+i,
        str(1000+i),
        42,
        42.0,
        # safepickle doesn't handle type==long
        #10121071034790721094712093712037123,
        None,
        True,
        b'qwertyuiop',
        # safepickle doesn't handle unicode
        #u'qwertyuiop',
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
        ('q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'),
        {'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'},
        #frozenset(['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']),
        {'e': 101, 'i': 105, 'o': 111, 'q': 113, 'p': 112,
         'r': 114, 'u': 117, 't': 116, 'w': 119, 'y': 121},
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', i],
        ('q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', i),
        {'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', i},
        # safepickle doesn't handle frozenset
        #frozenset(['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', i]),
        {'e': 101, 'i': 105, 'o': 111, 'q': 113, 'p': 112,
         'r': 114, 'u': 117, 't': 116, 'w': 119, 'y': 121, 'x': i},
    ] for i in range(1000)]

CANDIDATES = [
    ('pickle/2', lambda obj: pickle.dumps(obj, protocol=2), pickle.loads),
    ('cerealizer', cerealizer.dumps, cerealizer.loads),
    ('chopsticks.pencode', chopsticks.pencode.pencode, chopsticks.pencode.pdecode,),
    # DNF Used so many resources that whole machine ground to a halt
    #('gnosis', gnosis.xml.pickle.dumps, gnosis.xml.pickle.loads),
    ('safepickle', safepickle.dumps, safepickle.loads),
]

runner = perf.Runner()


if __name__ == '__main__':
    obj1 = setup()
    for name, dumps, loads in CANDIDATES:
        s = dumps(obj1)
        obj2 = loads(s)
        assert obj1 == obj2
        runner.timeit(
            name='%s dumps' % name,
            stmt='dumps(obj)',
            globals={'dumps': dumps, 'obj': obj1},
        )
        runner.timeit(
            name='%s loads' % name,
            stmt='loads(s)',
            globals={'loads': loads, 's': s},
        )
