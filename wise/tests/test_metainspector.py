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

class TestMetaInspector(unittest.TestCase):

    def setUp(self):
        pass

    def test_metainspector(self):
        import wise.meta_inspector

        # Check if the package database is init'd
        self.assertTrue(len(wise.meta_inspector.PACKAGES)>0)

        # Make sure the 'base' package is installed
        self.assertTrue('base' in wise.meta_inspector.PACKAGES.iterkeys())

if __name__ == '__main__':
    unittest.main()

#vim: ai ts=4 sts=4 et sw=4
