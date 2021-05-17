#!/usr/bin/env bash

URL_SSH=http://dataplane.org/sshclient.txt
URL_TELNET=http://dataplane.org/telnetlogin.txt
URL_VNC=http://dataplane.org/vncrfb.txt

OUTPUT=/mnt/data/logs/dataplane/$(date "%Y_%m_%d_%H_%M_%S").log

curl -s $URL_SSH >> $OUTPUT
curl -s $URL_TELNET >> $OUTPUT
curl -s $URL_VNC >> $OUTPUT


