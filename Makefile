.PHONY: test
test:
	python tests/test_dwdat2py.py -v

.PHONY: sdist
sdist:
	python setup.py sdist --formats=gztar,zip

.PHONY: install
install:
	pip install .

.PHONY: install-deps
install-deps:
	pip install -r requirements.txt

.PHONY: uninstall
uninstall:
	pip uninstall dwdat2py

# uninstall dependencies
.PHONY: uninstall-deps
uninstall-deps:
	pip uninstall -r requirements.txt

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
