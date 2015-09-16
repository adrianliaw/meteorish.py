
commands:
	@echo "develop"
	@echo "install"
	@echo "install-without-test"
	@echo "lint"
	@echo "test"
	@echo "clean"
	@echo "clean-pyc"
	@echo "clean-build"
	@echo "release"

develop: clean
	python setup.py develop

install-without-test:
	python setup.py install

install: clean test install-without-test

lint:
	pep8 meteorish tests

test: clean lint
	nosetests tests

clean: clean-pyc clean-build

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

release: test
	python setup.py sdist upload
