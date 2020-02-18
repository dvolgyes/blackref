#!/usr/bin/make

default:
	@echo "There is nothing to do."

test:
	python3 blackref_cli.py tests/test.bib

ci-test:
	python3 -m coverage run -a --source . blackref_cli.py -h
	python3 -m coverage run -a --source . blackref_cli.py tests/test.bib
	python3 -m coverage run -a --source . blackref_cli.py -w tests/test.bib
	python3 -m coverage run -a --source . blackref_cli.py -w -s year  tests/test.bib
	python3 -m coverage run -a --source . blackref_cli.py -o out.bib <tests/test.bib
	@echo "Testing is finished."

test-deploy:
	rm -fR build dist *egg-info
	python3 setup.py sdist bdist_wheel --universal
	twine upload -r pypitest dist/*
	pip3 install --user blackref --index-url https://test.pypi.org/simple/
	pip3 uninstall blackref
	rm -fR build dist *egg-info

deploy:
	rm -fR build dist *egg-info
	python3 setup.py sdist bdist_wheel --universal && twine upload -r pypi dist/*
	rm -fR build dist *egg-info
