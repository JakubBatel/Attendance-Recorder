build:
	pyenv exec python setup.py build

install-service:
	cp service/attendance-recoreder.service /etc/systemd/system/attendance-recoreder.service

install: build
	pyenv exec python setup.py install
	pyenv exec easy_install dist/*.egg

.PHONY: clean
clean:
	rm -rf dist build

.PHONY: install-test-dependency
install-test-dependency:
	if ! pyenv exec pip list | grep Flask; then pyenv exec pip install flask; fi

.PHONY: test
test: install-test-dependency
	pyenv exec python -m unittest tests/test_*.py