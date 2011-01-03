doc:
	pycco -p worksheet/*.py -d docs

all: cython

cython:
	$(MAKE) -C pure

clean: 
	-rm -f *.o *.pyc *.pyo *.html *.markdown *.out *.aux *.log *.pdf tags

clearcache:
	rm rules_cache object_cache rulesets_cache packages_cache
