#!/usr/bin/env bash

# all of these stem from https://www.shellcheck.net/wiki/
set -o pipefail  # propagate errors
set -u  # exit on undefined
set -e  # exit on non-zero return value
#set -f  # disable globbing/filename expansion
shopt -s failglob  # error on unexpaned globs
shopt -s inherit_errexit  # Bash disables set -e in command substitution by default; reverse this behavior

if [ "$1" = id_file ]; then
  grep IdentityFile ~/.colima/_lima/colima/ssh.config | awk -F '"' '{ print $2 }'
elif [ "$1" = port ]; then
  grep Port ~/.colima/_lima/colima/ssh.config | awk '{ print $2 }'
fi

