.PHONY: build
build:
	pyenv exec python setup.py build

.PHONY: create-venv
create-venv:
	pyenv virtualenv 3.8.1 attendance-recorder

.PHONY: install-service
install-service: create-venv
	cp service/attendance-recorder.service /etc/systemd/system/attendance-recorder.service

.PHONY: install
install: build
	pyenv exec python setup.py install
	pyenv exec easy_install dist/*.egg

.PHONY: all
all: install install-service
	systemctl enable attendance-recorder.service

.PHONY: clean
clean:
	rm -rf dist build

.PHONY: install-test-dependency
install-test-dependency:
	if ! pyenv exec pip list | grep Flask; then pyenv exec pip install flask; fi

.PHONY: test
test: install-test-dependency
	pyenv exec python -m unittest tests/test_*.py
