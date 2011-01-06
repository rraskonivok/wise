all: cython

cython:
	$(MAKE) -C pure

clean: 
#	-rm -f *.o *.pyc *.pyo *.html *.markdown *.out *.aux *.log *.pdf tags gunicorn.log
	$(MAKE) -C pure clean
	$(MAKE) -C cache clean

doc:
	pycco -p worksheet/*.py -d docs
