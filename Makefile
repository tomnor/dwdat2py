.PHONY: test
test:
	python tests/test_dwdat2py.py -v

.PHONY: clean
clean:
	rm -f *.pyc *.html
	rm -f dwdat2py/*.pyc
	rm -f tests/*d7d


README.html: README.rst
	rst2html README.rst README.html

browse_readme : README.html
	xdg-open README.html
