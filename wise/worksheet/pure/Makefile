all: 
	cython pure.pyx
	gcc -O3 -fPIC -c pure.c -I/usr/include/python2.6 -lpure
	gcc -shared pure.o -o pure.so -lpure

clean:
	rm -f *.so
	rm -f *.o
	rm -f *.pyc
