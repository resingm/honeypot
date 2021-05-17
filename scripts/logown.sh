#!/usr/bin/env bash

# ------------------------------------------------------------------
#
#   Root-own log files
#
# Each person who operates a honeypot gaines access to the non-sudo
# user "honey" in order to autoupload the logging data each night.
# To ensure transmitted data is kept secure, the script changes the
# ownership of the files.
#
# This solution is not perfect, but it is a good trade-off between
# configuration effort and data security.
#
# The script was written and published
#    by Max Resing <m.resing-1@student.utwente.nl>
#
# ------------------------------------------------------------------

LOG_DIR=/mnt/data/logs

find . -type f -print0 | xargs -o chown root:root
find . -type f -print0 | xargs -o chmod 644

