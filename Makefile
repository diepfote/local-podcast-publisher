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

