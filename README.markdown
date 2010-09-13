# Wise  
Copyright (C) 2010 Stephen Diehl (<sdiehl@clarku.edu>)

Licensed under the AGPLv3.

This is WISE an experimental math interface and simple
computer algebra system based on term rewriting. 

Originally I developed Wise to work with the Sage computer algebra 
system but instead moved over to the simpler and more robust
Pure language.

## Installation

Wise is *very* much alpha at this time but if you want to play
with it I reccomend you do so on Linux. I have not tested it on
any distro but Arch Linux but there shouldn't be any hurdles to
running it on any other distro.

In Arch Linux all dependencies can be built using the command

>    yaourt -S pure pure-gsl cython python django gunicorn

On any other Linux / BSD / Mac OSX:

1.  You'll need to install pure which depends on.
    
    - llvm version 2.7+
    - gsl
    - gmp
    - readline
    - make
    - gcc
    - bison
    - flex

    If you using OSX there is a MacPorts script [here](http://trac.macports.org/export/71406/trunk/dports/lang/pure/Portfile).
    
    Download and installation directions for building from source can be found here:
        
    <http://code.google.com/p/pure-lang/>
    <http://code.google.com/p/pure-lang/wiki/GettingStarted>

2.  You'll need to install Python2.6 and Cython which has no dependencies other than a C compiler such as gcc or clang. Directions can be found here:

    <http://www.cython.org/>

3.  You'll need gunicorn and django. If you have easy_install run:

    >   easy_install django

    >   easy_install gunicorn

    If not then you can find directions and source here:

    <http://gunicorn.org>

    <http://www.djangoproject.com>

4.  In a shell in the src directory run:
    >    python manage.py run_gunicorn 

    and point your browser to
    localhost:8000 . I see best performance in Chromium based
    browsers but Firefox works fine.

## Credits 

Wise depends/includes source from many open source projects. If I have used your source code and have not listed your project or name here please let me know.

* jQuery / jQuery UI - <http://jquery.com/>
* Django - <http://www.djangoproject.com/>
* django-reversion <http://code.google.com/p/django-reversion>
* web-app-theme <http://github.com/pilu/web-app-theme>
* Funcparserlib - <http://code.google.com/p/funcparserlib/>
* SHPAML - <http://shpaml.webfactional.com/>
* jQuery Hotkeys - <http://github.com/tzuryby/hotkeys>
* jQuery pnotify - <http://plugins.jquery.com/project/pnotify>
