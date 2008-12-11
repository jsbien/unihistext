
all::

all:: build/unihistext

build/unihistext: src/unihistext src/make-wrapper.sh src/gzip-wrapper.sh src/version.py
	mkdir -p `dirname $@`
	{ cd src && ./make-wrapper.sh unihistext version.py; } > $@
	chmod +x $@

src/version.py:
	{ echo "version = \"unknown\""; cd src && ./version-gen.sh | sed -e "s/^.*\$$/version = \"&\"/"; } > $@
.PHONY: src/version.py

clean:
	rm -rf build $(shell find -name '*~' | grep -v .git ) src/version.py
