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
    sudo systemctl stop tailscaled
    sudo systemctl stop sshd
    sudo pkill ssh
  # @TODO delete rule instead of restarting?
  # [root@frame ~]# nft add rule ip filter TCP tcp dport 80 accept
  # [root@frame ~]# nft -a list chain ip filter TCP
  # table ip filter {
  #         chain TCP { # handle 4
  #                 tcp dport 80 accept # handle 31
  #         }
  # }
  # [root@frame ~]# nft delete rule ip filter TCP handle 31
    sudo systemctl restart nftables

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
  port="$(./run-file-server-extract.sh port)"
  id_file="$(./run-file-server-extract.sh id_file)"
  set -x
  sudo ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "${port}" -f -NT -L podcast-svc-org:80:localhost:10080  lima@localhost -i "$id_file"

elif [ "$kernel" = Linux ]; then
  set -x
  sudo systemctl start tailscaled
  sudo systemctl start sshd
  sudo ssh -NT -f -i ~/.ssh/podman-remote -L frame:80:localhost:10080 "$USER"@localhost
  sudo nft add rule ip filter TCP tcp dport 80 accept

else
  exit 1
fi

  docker run --rm --name blub -p 10080:8080 \
  -v "$PWD"/etc/nginx/conf.d/default.conf:/etc/nginx/conf.d/default.conf \
  -v "$PWD":/data \
  -it \
  docker.io/library/nginx:1.27.2-alpine

