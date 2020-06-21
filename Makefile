PY := python3
PIP := pip3
TESTMODULES := test_wrappers test_init

TAGS: *.py */*.py
	etags $?

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
