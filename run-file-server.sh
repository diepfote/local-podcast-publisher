#!/usr/bin/env bash

# all of these stem from https://www.shellcheck.net/wiki/
set -o pipefail  # propagate errors
set -u  # exit on undefined
set -e  # exit on non-zero return value
#set -f  # disable globbing/filename expansion
shopt -s failglob  # error on unexpaned globs
shopt -s inherit_errexit  # Bash disables set -e in command substitution by default; reverse this behavior

kernel="$(uname)"
iptables_filename=/etc/iptables/iptables.rules

trap cleanup EXIT

cleanup () {
  if [ "$kernel" = Linux ]; then
    set -x
    sudo sed -i -r 's/^(.*INPUT.*10080.*)/#\1/' "$iptables_filename"
    set +x
  fi

  sudo -k
  set +x
}

if [ "$kernel" = Darwin ]; then
  # default lima port 60906
  # colima port: "$( grep Port ~/.colima/ssh_config  | awk '{ print $2 }' )"
  #
  # forward tailscale ip port 80 to localhost (lima vm)
  IP="$(grep -m 1 -rFi '"sshLocalPort":' ~/.lima/colima/ha.stdout.log | jq --raw-output .status.sshLocalPort)"
  set -x
  sudo ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "${IP}" -f -NT -L podcast-svc-org:80:localhost:10080  lima@localhost -i ~/.ssh/id_rsa

elif [ "$kernel" = Linux ]; then
  set -x
  sudo sed -i -r 's/^#(.*INPUT.*10080.*)/\1/' "$iptables_filename"
else
  exit 1
fi

docker run --rm --name blub -p 10080:8080 \
  -v "$PWD"/etc/nginx/conf.d/default.conf:/etc/nginx/conf.d/default.conf \
  -v "$PWD":/data \
  -it \
  docker.io/library/nginx:1.25.2-alpine

