SHELL := bash


# call like this:
# $ host="$(local-ip)" port=8080 make run-feed-generator
#
.PHONY: run-feed-generator
run-feed-generator:
	@ssh -p 60906 -f -NT -L ${host}:8080:localhost:8080  localhost
	source .venv/bin/activate; \
		./gistfile1.py ${host}:${port} tgs_podcast 'TGS Podcast'

.PHONY: install
install:
	deactivate; rm -r .venv; \
		virtualenv -p /usr/local/opt/python@3.9/bin/python3 .venv; \
		source .venv/bin/activate; \
		pip install -r requirements.txt

.PHONY: run-file-server
run-file-server:
	docker run --rm --name blub -p 8080:8080 \
		-v "$(shell pwd)"/etc/nginx/conf.d/default.conf:/etc/nginx/conf.d/default.conf \
		-v "$(shell pwd)":/data \
		-it \
		docker.io/library/nginx:1.21.3-alpine

