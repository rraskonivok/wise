JS_TARGETS := $(wildcard *.js)
JS_MINIFIED = $(JS_TARGETS:.js=.min.js)

all: js

js: $(JS_MINIFIED)

%.min.js: %.js
	yuicompressor $< >$@

clean:
	rm -f $(JS_MINIFIED)
