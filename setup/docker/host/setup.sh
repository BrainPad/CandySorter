#!/bin/sh
set -eu

if [ $# -lt 1 ]; then
  echo "Usage: `basename $0` [host_file]"
  exit 1
fi

cwd=$(dirname $0)

ansible-playbook \
  -u friday \
  --ask-su-pass \
  -i $1 \
  --connection=local \
  ${cwd}/site.yml
