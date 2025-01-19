SHELL := bash

.PHONY: run-file-server
run-file-server:
	./bin/run-file-server.sh

# calling convention -> README
#
.PHONY: run-feed-generator
run-feed-generator:
	source .venv/bin/activate; \
		./gistfile1.py "${host}":"${port}" "${dir_to_expose}" "${title}"

.PHONY: install
install:
	deactivate; rm -r .venv; \
		virtualenv -p python3 .venv; \
		source .venv/bin/activate; \
		pip install -r requirements.txt

