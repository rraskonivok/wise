PACKAGENAME = pkgtemplate # the name of the pkg, normally the folder name as well
SRCS       := pkgtepmlate.pure  # your pure source files

all: annotate doc

annotate:
	pycco -p *.py -d ../$(PACKAGENAME)/docs

puredoc:
	pycco -p *.pure -d ../$(PACKAGENAME)/docs

clean: 
	-rm -f *.o *.pyc *.pyo *.html
