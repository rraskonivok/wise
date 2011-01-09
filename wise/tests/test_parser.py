#!/usr/bin/env python

import unittest

# --- Begin Test Setup ---
from django.core.management import setup_environ
import settings
setup_environ(settings)
settings.DEBUG = True
from wise import boot
from wise import *
boot.start_python_pure()
boot.start_cython()
# --- End Test Setup ---

from wise.translators.pytopure import parse_sexp, sexp_parse

class TestParser(unittest.TestCase):

    def setUp(self):
        pass

    def test_sexp_parser(self):
        self.assertIsNotNone(sexp_parse('(a b c)'))
        self.assertIsNotNone(sexp_parse('(a 2 (f a 3.5))'))
        self.assertIsNotNone(sexp_parse('(f (f (f x)))'))

        with self.assertRaises(Exception):
            sexp_parse('(a b c')

        with self.assertRaises(Exception):
            sexp_parse('a b c')

    def test_sexp_tuple(self):
        parsed = sexp_parse('(f (g (h x)))')
        self.assertEqual(parsed, ('f', [('g', [('h', ['x'])])]))

        # First inner sexp
        head, args = parsed
        self.assertEqual(head, 'f')
        self.assertEqual(len(args),1)
        # Second inner sexp
        head, args = args[0]
        self.assertEqual(head, 'g')
        self.assertEqual(len(args),1)

    def test_sexp_tuples(self):
        tests = [
            ('(a)'         ,  ('a', [])                          ),
            ( '(a b c)'    ,  ('a', ['b', 'c'])                  ),
            ( '(f 1 2)'    ,  ('f', [1, 2])                      ),
            ( '(f 1.1 2.5)',  ('f', [1.1, 2.5])                  ),
            ( '(f (g (x)))',  ('f', [('g', [('x', [])])])        ),
        ]

        for sexp, output in tests:
            self.assertEqual(sexp_parse(sexp), output)


if __name__ == '__main__':
    unittest.main()

#from translators.parser import pure_parse, sexp_parse
#from funcparserlib.util import pretty_tree

#def is_number(s):
    #''' Return true if the given string argument can be cast into
    #a numeric type'''
    #try:
        #float(s)
    #except ValueError:
        #return False
    #return True

#class Branch(object):

    #def __init__(self, head, args=[]):
        #self.head = head
        #self.args = args

    #def __repr__(self):
        #return '(%r,%r)' % (self.head, self.args)

#def ptree(t):
    #def kids(x):
        #if isinstance(x, Branch):
            #return x.args
        #else:
            #return []
    #def show(x):
        #if isinstance(x, Branch):
            #return str(x.head)
        #else:
            #return repr(x)
    #return pretty_tree(t, kids, show)

#def map_to_sexp(parsed):
    #if isinstance(parsed,tuple):
        #head = parsed[0]
        #args = parsed[1]

        #return Branch(head, [map_to_sexp(arg) for arg in args])
    #else:
        #atom = parsed
        #if is_number(atom):
            #return Branch('num',[atom])
        #elif atom == 'ph':
            #return Branch('ph',[])
        #else:
            #return Branch('var',[atom])

#def make_sexp(parsed):
    #if isinstance(parsed,tuple):
        #head = parsed[0]
        #args = parsed[1]

        #return Branch(head, [make_sexp(arg) for arg in args])
    #else:
        #return parsed

#def ParseTree(s, parser):
    #if parser == 'sexp':
        #parsed = sexp_parse(s)
        #return make_sexp(parsed)

    #elif parser == 'pure':
        #parsed = pure_parse(s)
        #return map_to_sexp(parsed)

#pprint = lambda x: ptree(map_to_sexp(x))

#tests = ['f 1',
         #'eq (add x y) (add 1 x)',
         #'abc 5 ph',
         #'abc 150',
         #'abc (f 150) 3.1',
         #'add (-25) (25)',
         #'f (f (f x))',
         #]

#for test in tests:
    #print ParseTree(test,'pure')
    #print pprint(result)

#tests = ["(Equation a b)",
#         "( Equation ( Addition ( Variable x ) ( Numeric 25 ) ) ( Variable y ) )",
#         "( Equation ( Addition ( Numeric 3 ) ( Numeric 1 ) ) ( Variable y ) )",
#         "(Placeholder )",
#         "(Numeric  2)",
#         "( Equation ( Rational ( Numeric 1 ) ( Product ( Addition ( Sqrt ( Product ( Sqrt ( Numeric 5 ) ) ( Variable phi ) ) ) ( Negate ( Variable phi ) ) ) ( Power ( Variable e ) ( Product ( Rational ( Numeric 2 ) ( Numeric 5 ) ) ( Variable pi ) ) ) ) ) ( Addition ( Numeric 1 ) ( Rational ( Power ( Variable e ) ( Negate ( Product ( Numeric 2 ) ( Variable pi ) ) ) ) ( Addition ( Numeric 1 ) ( Rational ( Power ( Variable e ) ( Negate ( Product ( Numeric 4 ) ( Variable pi ) ) ) ) ( Addition ( Numeric 1 ) ( Rational ( Power ( Variable e ) ( Negate ( Product ( Numeric 6 ) ( Variable pi ) ) ) ) ( Addition ( Numeric 1 ) ( Rational ( Power ( Variable e ) ( Negate ( Product ( Numeric 8 ) ( Variable pi ) ) ) ) ( Addition ( Numeric 1 ) ( Placeholder ) ) ) ) ) ) ) ) ) ) )"
#        ]
##
#for test in tests:
#    print ParseTree(test,'sexp')
#    #print pprint(result)
