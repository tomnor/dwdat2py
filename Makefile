PY := python3
PIP := pip3
TESTMODULES := test_wrappers test_init

# "normal" assignment:
TAGRX1 := '/[ \t]*\([^ \t]+\)[ \t]*=[ \t]*[^ \t]+/\1/'
# the first of unpacked variables:
TAGRX2 := '/[ \t]*\([^ \t]+\), *[^=]+?=[ \t]*[^ \t]+/\1/'
# "normal" import
TAGRX3 := '/[ \t]*import[ \t]+\([^ \t]+\)\>/\1/'
# from m import ...:
TAGRX4 := '/[ \t]*from +[^ \t]+ +import +\([^ \t]+\)/\1/'

tags : TAGS
TAGS : *.py */*.py
	etags --regex=$(TAGRX1) --regex=$(TAGRX2) --regex=$(TAGRX3) \
	      --regex=$(TAGRX4) $^

.PHONY: test
test:
	cd tests && $(PY) -m unittest -v $(TESTMODULES)

dist: *.py */*.py CHANGES.rst README.rst
	$(PY) setup.py sdist bdist_wheel

release: dist
	twine upload dist/*

.PHONY: install
install:
	$(PIP) install .

.PHONY: uninstall
uninstall:
	$(PIP) uninstall dwdat2py

README.html: README.rst
	rst2html README.rst README.html

CHANGES.html: CHANGES.rst
	rst2html CHANGES.rst CHANGES.html

.PHONY: see-html
see-html: README.html CHANGES.html
	see README.html CHANGES.html

.PHONY: clean
clean:
	rm -f *.pyc *.html
	rm -f dwdat2py/*.pyc
	rm -f tests/*d7d
	rm -rf build *.egg-info dist
	rm -f MANIFEST
