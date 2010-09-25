PACKAGENAME = logic
SRCS    := logic.pure

all: annotate doc

annotate:
	pure --ctags ${SRCS}
	../annotate.py ${SRCS} > $(PACKAGENAME).py
	rm tags

docs:
	pure-doc *.pure > $(PACKAGENAME).rst

html: doc
	rst2html.py $(PACKAGENAME).rst > $(PACKAGENAME).html

latex: doc
	rst2latex.py $(PACKAGENAME).rst > $(PACKAGENAME).tex 
	pdflatex $(PACKAGENAME).tex

clean: 
	-rm -f *.o *.pyc *.pyo *.html *.rst *.out *.aux *.log *.pdf tags
