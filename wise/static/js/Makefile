JS_TARGETS := $(wildcard *.js)
JS_MINIFIED = $(JS_TARGETS:.js=.min.js)

all: js

js: $(JS_MINIFIED)

%.min.js: %.js
	yuicompressor $< >$@

all.js:
	cat > $@ $(JS_TARGETS)

all-min.js: $(JS_MINIFIED)
	cat > $@ $^

clean:
	rm -f $(JS_MINIFIED)
