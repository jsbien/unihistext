all::

TMPVERSIONFILE := $(shell echo /tmp/.tmpverfile-`whoami`)

all:: update_version


ADDDEPS := src/version.py src/helpers.py

build/unihistext: src/unihistext src/unihistext.py src/unicode_blocks.py $(ADDDEPS)
all:: build/unihistext
build/uninormalize: src/uninormalize src/uninormalize.py $(ADDDEPS)
all:: build/uninormalize

install:
	install --group=root --owner=root \
	    build/unihistext build/uninormalize $(DESTDIR)/usr/bin

deb:
	debuild

build/uninormalize build/unihistext:
	mkdir -p `dirname $@`
	./scripts/make-wrapper.sh $^ > $@
	chmod +x $@

update_version: $(TMPVERSIONFILE)
	cmp $(TMPVERSIONFILE) src/version.py -s || mv $(TMPVERSIONFILE) src/version.py
.PHONY: $(TMPVERSIONFILE)

$(TMPVERSIONFILE) src/version.py:
	{ echo "version = \"unknown\""; ./scripts/version-gen.sh | sed -e "s/^.*\$$/version = \"&\"/"; } > $@
#.PHONY: src/version.py

clean:
	rm -rf build $(shell find -name '*~' -o -name '*.pyc' -o -name '*.pyo' | grep -v .git ) src/version.py $(TMPVERSIONFILE)
