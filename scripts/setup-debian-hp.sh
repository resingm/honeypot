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
CONFIG_SSH=/etc/ssh/sshd_config
CONFIG_TEL=/etc/inetd.conf
CONFIG_VNC=/etc/systemd/system/vncservice.service
CONFIG_LOG=/etc/logrotate.conf
VNC_SERVICE=vncservice.service

URL_SSH=https://static.maxresing.de/pub/sshd_config
URL_TEL=https://static.maxresing.de/pub/inetd.conf
URL_VNC=https://static.maxresing.de/pub/vncservice


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
echo "Setup SSH honeypot:"
echo "  * Installing SSH server (openssh-server)"
apt-get -qq install openssh-server

echo "  * Backup ${CONFIG_SSH}"
cp ${CONFIG_SSH} ${CONFIG_SSH}.bak

echo "  * Download Configuration sshd_config"
curl -o ${CONFIG_SSH} ${URL_SSH}

echo "  * Enable sshd.service"
systemctl enable sshd.service

echo "Successfully set up SSH honeypot"
echo ""


# --- Setup telnet honeypot ----------------------------------------
echo "Setup Telnet honeypot:"

echo "  * Installing telnet server (telnetd)"
apt-get -qq install inetutils-telnetd

echo "  * Backup ${CONFIG_TEL}"
cp ${CONFIG_TEL} ${CONFIG_TEL}.bak

echo "  * Download inetd.conf"
curl -o ${CONFIG_TEL} ${URL_TEL}


echo "  * Enable inetd.service"
systemctl enable inetd.service

echo "Successfully set up Telnet honeypot"
echo ""


# --- Setup VNC honeypot -------------------------------------------

echo "Setup VNC honeypot:"

echo "  * Installing vncterm"
apt-get -qq install linuxvnc

echo "  * Download unit file"
curl -o ${CONFIG_VNC} ${URL_VNC}

echo "  * Enable ${VNC_SERVICE}"
systemctl enable ${VNC_SERVICE}

echo "Successfully setup VNC honeypot"
echo ""

# --- Setup Logrotation --------------------------------------------

echo "Setup logrotate:"

echo "  * "
echo "  * "
echo "  * "

echo "Successfully setup logrotate"
echo ""


# --- Setup Cronjobs -----------------------------------------------



# --- Cleanup ------------------------------------------------------





