all: cython

cython:
	$(MAKE) -C pure

clean: 
	-rm -f *.o *.pyc *.pyo *.html *.markdown *.out *.aux *.log *.pdf tags gunicorn.log

clearcache:
	rm rules_cache rulesets_cache packages_cache

doc:
	pycco -p worksheet/*.py -d docs
