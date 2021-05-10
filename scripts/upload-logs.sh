#!/bin/bash
# ------------------------------------------------------------------
#
# Transmit logged data
#
# Script to extract logging information from the auth & syslog and
# transmit those logs to the central database server max.dnsjedi.org
#
# ------------------------------------------------------------------


SEMAPHORE=transmit-logs

# --- Semaphore locking --------------------------------------------

LOCK=/tmp/${SEMAPHORE}.lock

if [ -f "$LOCK" ] ; then
  echo "Script is already running"
  exit 1
fi

trap "rm -f $LOCK" EXIT
touch $LOCK

# --- Extract logs -------------------------------------------------

LOG_SSH=/var/log/auth.log.1
LOG_TELNET=/var/log/syslog.1
LOG_VNC=/var/log/syslog.1

LOG_DIR=/var/log/honeypot
LOG_OUT=${LOG_DIR}/$(date +"%Y_%m_%d_%H_%M_%S").log

REMOTE_USER=honey
REMOTE_DIR=/mnt/data/logs


# Create directory and file
mkdir -p ${LOG_DIR}
touch ${LOG_DIR}/${LOG_OUT}

# Extract SSH logs
cat ${LOG_SSH} | grep "sshd" >> ${LOG_OUT}

# Extract Telnet logs
cat ${LOG_TELNET} | grep "telnetd" >> ${LOG_OUT}

# Extract VNC logs

cat ${LOG_VNC} | grep "linuxvnc" >> ${LOG_OUT}

# --- Transmit logs ------------------------------------------------

scp ${LOG_OUT} ${REMOTE_USER}@${REMOTE_DIR}

