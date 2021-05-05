#!/bin/bash

# ------------------------------------------------------------------
#
# 
#
# by Max Resing <m.resing-1@student.utwente.nl>
#
# ------------------------------------------------------------------

SEMAPHORE=honeypotsetup
VERSION=0.1.0

# TODO: Add usage
USAGE="Usage: $0 [-vh]"

# Flags

# Constants
CONFIG_SSH = /etc/ssh/sshd_config
CONFIG_TEL = /etc/telnet/config
CONFIG_VNC = /etc/tigervnc/config


# --- Option processing --------------------------------------------
#if [ $# == 0 ] ; then
#  echo $USAGE
#  exit 1;
#fi

while getopts "vh?" opt; do
  case $opt in
    v)
      echo "Version $VERSION"
      exit 0;
      ;;
    h)
      echo $USAGE
      exit 0;
      ;;
    ?)
      echo "Unkown option $OPTARG"
      exit 0;
      ;;
    :)
      echo "No argument value for option $OPTARG"
      exit 0;
      ;;
    *)
      echo "Unkown error while processing options"
      exit 0;
      ;;
  esac
done


# --- Semaphore locking --------------------------------------------

LOCK=/tmp/${SEMAPHORE}.lock

if [ -f "$LOCK" ] ; then
  echo "Script is already running"
  exit 1
fi

trap "rm -f $LOCK" EXIT
touch $LOCK


# --- Script -------------------------------------------------------

# Check if script runs with super user permissions
if [[ $(id -u) -ne 0 ]] ; then
  echo "Script can not be executed without super user permissions"
  echo "Try again executing 'sudo $0'"
  exit 1
fi


echo "Performing general setup tasks:"

echo "  * Updating system"
apt-get -qq update
apt-get -qq dist-upgrade

# echo "  * Installing curl"
# apt-get -qq install curl


# --- Setup SSH honeypot -------------------------------------------
echo "Setup SSH Honeypot:"
echo "  * Installing SSH server (openssh-server)"
apt-get -qq install openssh-server

echo "  * Backup ${CONFIG_SSH}"
cp ${CONFIG_SSH} ${CONFIG_SSH}.bak

echo "  * Configure sshd"
echo "" > ${CONFIG_SSH}
echo "# ------------------------------------------------------------------" >> ${CONFIG_SSH}
echo "# " >> ${CONFIG_SSH}
echo "#   Configuration generated" >> ${CONFIG_SSH}
echo "# " >> ${CONFIG_SSH}
echo "#   In case of questions, contact Max Resing <m.resing-1@student.utwente.nl>" >> ${CONFIG_SSH}
echo "# " >> ${CONFIG_SSH}
echo "# ------------------------------------------------------------------" >> ${CONFIG_SSH}
echo "" >> ${CONFIG_SSH}
echo "Include /etc/ssh/sshd_config.d/*.conf" >> ${CONFIG_SSH}
echo "" >> ${CONFIG_SSH}
echo "# Listening" >> ${CONFIG_SSH}
echo "" >> ${CONFIG_SSH}
echo "Port 22" >> ${CONFIG_SSH}
echo "Address Family any" >> ${CONFIG_SSH}
echo "ListenAddress 0.0.0.0" >> ${CONFIG_SSH}
echo "" >> ${CONFIG_SSH}
echo "# Authentication" >> ${CONFIG_SSH}
echo "" >> ${CONFIG_SSH}
echo "PermitRootLogin prohibit-password" >> ${CONFIG_SSH}
echo "PubkeyAuthentication yes" >> ${CONFIG_SSH}
echo "PasswordAuthentication yes" >> ${CONFIG_SSH}
echo "" >> ${CONFIG_SSH}
echo "ChallengeResponseAuthentication no" >> ${CONFIG_SSH}
echo "UsePAM yes" >> ${CONFIG_SSH}
echo "X11Forwarding yes" >> ${CONFIG_SSH}
echo "PrintMotd no" >> ${CONFIG_SSH}
echo "Accept Env LANG LC_*" >> ${CONFIG_SSH}
echo "Subsystem   sftp    /usr/lib/openssh/sftp-server" >> ${CONFIG_SSH}
echo "" >> ${CONFIG_SSH}


echo "  * Enable sshd.service"
systemctl enable sshd.service

echo ""

# --- Setup telnet honeypot ----------------------------------------
echo "Setup Telnet Honeypot:"

echo "  * Installing telnet server (telnetd)"
apt-get -qq install telnetd

echo "  * Backup ${CONFIG_TEL}"
cp ${CONFIG_TEL} ${CONFIG_TEL}.bak

echo "  * Configure telnetd"
# TODO: Configure telnetd

echo "  * Enable sshd.service"
systemctl enable telnetd.service

echo ""

# --- Setup VNC honeypot -------------------------------------------

echo ""

# --- Setup Logrotation --------------------------------------------
