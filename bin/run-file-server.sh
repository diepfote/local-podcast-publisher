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
  docker stop -f blub || true
  sudo ~/.cargo/bin/killport 80

  if [ "$kernel" = Linux ]; then
    set -x
    sudo systemctl stop tailscaled
    sudo "$HOME"/.cargo/bin/killport 80
    sudo systemctl stop sshd
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
  port="$("$(dirname "$0")"/run-file-server-extract.sh port)"
  id_file="$("$(dirname "$0")"/run-file-server-extract.sh id_file)"

  # taken care of by ./port-forward-80
  # set -x
  # sudo ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "${port}" -f -NT -L mac:80:localhost:10080  lima@localhost -i "$id_file"

elif [ "$kernel" = Linux ]; then
  set -x
  sudo systemctl start tailscaled
  sudo systemctl start sshd
  sudo nft add rule ip filter TCP tcp dport 80 accept

  # ---------------------------------
  # this step could not be automated:
  # we need to run `sudo killport 80` & run this after this script starts the container
  set +x
  source ~/Documents/scripts/source-me/colors.sh  || true
  echo -e "${RED}Please run this after the container starts$NC:"
  echo -n "$YELLOW"
  echo 'sudo killport 80'
  echo 'sudo /usr/bin/ssh -NT -f -i ~/.ssh/podman-remote -L frame:80:localhost:10080 "$USER"@localhost'
  echo -n "$NC"
  sleep 5
  set -x
  # ---------------------------------

else
  exit 1
fi

docker run --rm --name blub -p 10080:8080 \
  -v "$PWD"/etc/nginx/conf.d/default.conf:/etc/nginx/conf.d/default.conf \
  -v "$PWD":/data \
  "$(cat nginx-image.txt)"  &

sleep 10

if [ "$kernel" = Darwin ]; then
  alacritty -e "$(realpath "$(dirname "$0")")"/port-forward-80 "$id_file" "$port"
else
  "$(dirname "$0")"/port-forward-80
fi

