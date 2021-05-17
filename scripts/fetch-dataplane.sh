#!/usr/bin/env bash

# ------------------------------------------------------------------
#
#   Download Dataplane.org data
#
# The script is supposed to download and store the dataplane.org
# data feeds. It downloads the following three feeds:
#
#   * SSH client connection
#   * TELNET login
#   * VNC RFB
#
# The data is stored in the specified directory. The file name is
# the date and time the data was acquired.
#
# The script was written and published
#    by Max Resing <m.resing-1@student.utwente.nl>
#
# ------------------------------------------------------------------

URL_SSH=http://dataplane.org/sshclient.txt
URL_TELNET=http://dataplane.org/telnetlogin.txt
URL_VNC=http://dataplane.org/vncrfb.txt

OUTPUT_DIR=/mnt/data/logs/dataplane
OUTPUT_FILE=$(date +"%Y_%m_%d_%H_%M_%S").log

mkdir -p $OUTPUT_DIR

curl -s $URL_SSH >> ${OUTPUT_DIR}/${OUTPUT_FILE}
curl -s $URL_TELNET >> ${OUTPUT_DIR}/${OUTPUT_FILE}
curl -s $URL_VNC >> ${OUTPUT_DIR}/${OUTPUT_FILE}

