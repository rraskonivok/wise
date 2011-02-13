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

from wise.translators.pytopure import (parse_sexp, sexp_parse,
        make_sexp, parse_pure_exp, pure_parse)
from wise.packages import loader

base_objects = loader.load_package_module('base','objects')

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
            ( '(f 0 -1)'   ,  ('f', [0, -1])                     ),
            ( '(f (g (x)))',  ('f', [('g', [('x', [])])])        ),
        ]

        for sexp, output in tests:
            parsed = sexp_parse(sexp)
            mapped = make_sexp(parsed)
            self.assertEqual(parsed, output)
            self.assertEqual(len(mapped.args), len(output[1]))

    def test_sexp_mapping(self):
        good_sexps = [
            '( Addition ( Variable x ) ( Variable y ) )',
            '( Variable x )',
            '( Equation 1 1 )',
            '( Placeholder )',
            '( Numeric 3.14159 )',
        ]

        bad_sexps = [
            '( Variable 1 )',
            '( Numeric x )',
            '( Numeric 1 1 )',
            '( Equation foo )',
            '( Addition )',
        ]

        for sexp in good_sexps:
            self.assertIsNotNone(parse_sexp(sexp))

        for sexp in bad_sexps:
            with self.assertRaises(Exception):
                parsed = parse_sexp(sexp)

    def test_sexp_mapping_types(self):
        good_sexps = [
        ( '( Addition ( Variable x ) ( Variable y ))',base_objects.Addition),
        ( '( Variable x )', base_objects.Variable) ,
        ]
        for sexp, cls in good_sexps:
            parsed = parse_sexp(sexp)
            self.assertEqual(parsed.classname, cls.__name__)

    def test_pure_lists(self):
        tests = [
            ('f x',            ('f', ['x']) ),
            ('f x y',          ('f', ['x', 'y']) ),
            ('f x (f x y)',    ('f', ['x', ('f',['x','y'])]) ),
            ('f (f x y) x',    ('f', [('f',['x','y']),'x']) ),
            ('[1,2,3]',        [1,2,3] ),
            ('f [1,2,3]',      ('f', [[1,2,3]]) ),
            ('f [1,2,3] x',    ('f', [[1,2,3],'x']) ),
            ('f y [1,2,3]',    ('f', ['y',[1,2,3]]) ),
            ('1',              1  ),
            ('[x,y,z]',        ['x','y','z']  ),
            ('[f x,y,z]',      [('f',['x']),'y','z']  ),
            ('[x,f y,z]',      ['x',('f',['y']),'z']  ),
            ('[x,f x 1L,z]',   ['x',('f',['x',1L]),'z']  ),

        ]
        for sexp, output in tests:
            self.assertEqual(pure_parse(sexp), output)

    def test_pure_mapping(self):

        tests = [
            (    '[x,y]', '(Tuple (Variable x) (Variable y))' ),
            (    '[x,1]', '(Tuple (Variable x) (Numeric 1))' ),
        ]

        for sexp, output in tests:
            self.assertIsNotNone(parse_pure_exp(sexp))

if __name__ == '__main__':
    unittest.main()
