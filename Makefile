.PHONY: test
test:
	python3 tests/test_wrappers.py -v

.PHONY: dist
dist:
	python setup.py sdist bdist_wheel

.PHONY: install
install:
	pip install .

.PHONY: uninstall
uninstall:
	pip uninstall dwdat2py

README.html: README.rst
	rst2html README.rst README.html

browse_readme: README.html
	xdg-open README.html

.PHONY: clean
clean:
	rm -f *.pyc *.html
	rm -f dwdat2py/*.pyc
	rm -f tests/*d7d
	rm -rf build *.egg-info dist
	rm -f MANIFEST
