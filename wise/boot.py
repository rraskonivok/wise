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

# Note: All these functions are idempotent unless you specify
# force=True, i.e running them multiple times won't create
# multiple lookup tables or start multiple interpreters

def start_python_pure():
    """ Load all Python packages and initialize the Pure-Cython
    wrapper. Potentially a very long operation """

    from wise.translators.mathobjects import (build_python_lookup,
        build_pure_lookup, build_transform_lookup)

    build_python_lookup()
    build_pure_lookup()
    build_transform_lookup()

    logger.info('Started Pure+Python Session')


def start_cython():
    """ Load all Python packages and initialize the Pure-Cython
    wrapper. Potentially a very long operation """

    from wise.translators.pure_wrap import init_pure
    from wise.translators.mathobjects import (build_cython_objects,
            build_rule_lookup)

    # ORDER IS VERY IMPORTANT
    init_pure()
    build_cython_objects()
    build_rule_lookup()

    logger.info('Started Cython Interface')

def start_django():
    from django.core.management import setup_environ
    import settings
    setup_environ(settings)
    settings.DEBUG = True
