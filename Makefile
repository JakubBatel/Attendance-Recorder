build:
	python setup.py build

install: build
	python setup.py install
	easy_install dist/*.egg

.PHONY: clean

clean:
	rm -rf dist build