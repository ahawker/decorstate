.PHONY: clean-pyc test tox

all: clean-pyc test

test:
	py.test

tox:
	tox

clean-pyc:
	find . -iname '*.pyc' -exec rm -f {} +
	find . -iname '*.pyo' -exec rm -f {} +
	find . -iname '*.~' -exec rm -f {} +
