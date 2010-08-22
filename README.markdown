# Wise  
Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>  
Licensed under the AGPLv3.  

This is WISE an experimental math interface and simple
computer algebra system based on term rewriting. 

Originally I developed it work with the Sage computer algebra 
system but instead moved over to the simple and more robust
Pure language.

## Installation

It is *very* much alpha at this time but if you want to play
with it I reccomend you do so on Linux. I have not tested it on
any distro but Arch Linux but there shouldn't be any hurdles to
running it on any other distro. Some instructions:

1.  You'll need to install pure which depends on.
    
    - llvm version 2.7+
    - gsl
    - gmp
    - readline
    - make
    - gcc
    - bison
    - flex
    
    Download and installation directions can be found here:
        
         <http://code.google.com/p/pure-lang/>

2.  You'll need to install Python2.6.x

3.  You'll need gunicorn. If you have easy_install run

	 easy_install gunicorn

    If not then you can find directions here:

	 <http://gunicorn.org/>

4.  Run python manage.py run_gunicorn and point your browser to
    localhost:8000 . I see best performance in Chromium based
    browsers but Firefox works fine.

## Credits 

* jQuery / jQuery UI - <http://jquery.com/>
* Django - <http://www.djangoproject.com/>
* Funcparserlib - <http://code.google.com/p/funcparserlib/>
* SHPAML - <http://shpaml.webfactional.com/>
* jQuery Hotkeys - <http://github.com/tzuryby/hotkeys>
* jQuery layout - <http://layout.jquery-dev.net/>
* jQuery pnotify - <http://plugins.jquery.com/project/pnotify>
