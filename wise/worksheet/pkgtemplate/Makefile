PACKAGENAME = pkgtemplate # the name of the pkg, normally the folder name as well
SRCS       := template.pure  # your pure source files

all: annotate doc

annotate:
	pure --ctags ${SRCS}
	../annotate.py ${SRCS} > $(PACKAGENAME).py
	rm tags

doc:
	pure-doc *.pure > $(PACKAGENAME).markdown

html: doc
	rst2html.py $(PACKAGENAME).markdown > $(PACKAGENAME).html

latex: doc
	rst2latex.py $(PACKAGENAME).markdown > $(PACKAGENAME).tex 
	pdflatex $(PACKAGENAME).tex

clean: 
	-rm -f *.o *.pyc *.pyo *.html *.markdown *.out *.aux *.log *.pdf tags
