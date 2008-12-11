
all::

all:: build/unihistext

build/unihistext: src/unihistext src/make-wrapper.sh src/gzip-wrapper.sh
	mkdir -p `dirname $@`
	{ cd src && ./make-wrapper.sh unihistext; } > $@
	chmod +x $@

clean:
	rm -rf build $(shell find -name '*~' | grep -v .git )
