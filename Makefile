SHELL := bash

.PHONY: run-file-server
run-file-server:
	# sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80
	sudo -k
	docker run --rm --name blub -p 8080:8080 \
		-v "$(shell pwd)"/etc/nginx/conf.d/default.conf:/etc/nginx/conf.d/default.conf \
		-v "$(shell pwd)":/data \
		-it \
		docker.io/library/nginx:1.21.3-alpine


# call like this:
# $ host="$(local-ip)" port=8080 make run-feed-generator
#
.PHONY: run-feed-generator
run-feed-generator:
	source .venv/bin/activate; \
		./gistfile1.py "${host}":"${port}" "${dir_to_expose}"/ "${title}"

.PHONY: install
install:
	deactivate; rm -r .venv; \
		virtualenv -p python3 .venv; \
		source .venv/bin/activate; \
		pip install -r requirements.txt

