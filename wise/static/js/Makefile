COFFEE_SRC := $(wildcard *.coffee)
JS_TARGETS := $(wildcard *.js)
JS_MINIFIED = $(JS_TARGETS:.js=.min.js)

all: js

coffee: $(COFFEE_SRC)

js: $(JS_MINIFIED)

%.min.js: %.js
	yuicompressor $< >$@

%.js: %.js
	coffee $< >$@

all.js:
	cat > $@ $(JS_TARGETS)

all-min.js: $(JS_MINIFIED)
	cat > $@ $^

clean:
	rm -f $(JS_MINIFIED)
