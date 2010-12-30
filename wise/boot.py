# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from worksheet.utils import logger

# No wise includes up here, load everyting lazily

# Note: All these functions are nilpotent unless you specify
# force=True, i.e running them multiple times won't create
# multiple lookup tables or start multiple interpreters

def start_python_pure():
    """ Load all Python packages and initialize the Pure-Cython
    wrapper. Potentially a very long operation """

    from wise.translators.mathobjects import build_all_lookup

    build_all_lookup()

    logger.info('Started Pure+Python Session')

def start_cython():
    """ Load all Python packages and initialize the Pure-Cython
    wrapper. Potentially a very long operation """

    from wise.translators.mathobjects import build_cython_objects

    build_all_lookup()

    logger.info('Started Pure+Python Session')
