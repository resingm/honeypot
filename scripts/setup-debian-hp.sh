#!/bin/bash

# ------------------------------------------------------------------
#
# Setup script to automate the setup of a honeypot
#
# The script aims to automate the task of setting up a debian-based
# honeypot. The honeypot will operate an SSH server, a Telnet server
# and a VNC server (vncterm). The services will be served on their
# default ports 22 (SSH), 23 (Telnet) and 5900 (VNC). Furthermore,
# logrotation will be reconfigured, such that the two log files will
# rotate each night. The log files will be filtered and transfered
# to a central server each night.
#
# Log files:
#  /var/log/auth.log -> sshd
#  /var/log/syslog   -> telnetd, linuxvnc
#
# If you have any remarks on the script or any feedback, please do
# not hesitate to contact the author of this script.
#
# The script was written and published
#    by Max Resing <m.resing-1@student.utwente.nl>
#
# ------------------------------------------------------------------

SEMAPHORE=honeypotsetup
VERSION=0.1.0

# TODO: Add usage
USAGE="Usage: $0 [-vh]"

# Flags

# Constants
DOTENV=/etc/honeypot/.env
DIRECTORY=/etc/honeypot/
VNC_SERVICE=vncservice.service

CONFIG_SSH=/etc/ssh/sshd_config
CONFIG_TEL=/etc/inetd.conf
CONFIG_VNC=/etc/systemd/system/vncservice.service
CONFIG_LOG=/etc/logrotate.conf

URL_SSH=https://static.maxresing.de/pub/sshd_config
URL_TEL=https://static.maxresing.de/pub/inetd.conf
URL_VNC=https://static.maxresing.de/pub/vncservice
URL_LOG=https://static.maxresing.de/pub/logrotate.conf

SSH_KEY=/home/${SUDO_USER}/.ssh/id_honeypot


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

echo "  * Create honeypot directory"
mkdir -p ${DIRECTORY}

echo "  * Create .env file"
# Clean possibly existing .env from previous executions
echo "" > ${DOTENT}

echo "  * Updating system"
apt-get -qq update
apt-get -qq dist-upgrade

# echo "  * Installing curl"
# apt-get -qq install curl


# --- Setup SSH honeypot -------------------------------------------

echo "Requires user input"
echo "If you have any doubts, please cancel the execution with CTRL+C"
echo "and contact m.resing-1@student.utwente.nl"
echo ""
echo "Questions (2):"
echo "  * Which category does the honeypot belong to?"
echo "    [campus, cloud, residential]"
read hp_cat

echo "  * Which honeypot ID did you get assigned?"
echo "    [number >= 0]"
read hp_id

echo "HP_CATEGORY=${hp_cat}" >> ${DOTENV}
echo "HP_ID=${hp_id}" >> ${DOTENV}


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

echo "  * Backup configuration"
cp ${CONFIG_LOG} ${CONFIG_LOG}.bak

echo "  * Download configuration file"
curl -o ${CONFIG_LOG} ${URL_LOG}

echo "Successfully setup logrotate"
echo ""


# --- Setup SSH Keys -----------------------------------------------

echo "Setup SSH key:"

echo "  * Generate Key"
ssh-keygen -t ed25519 -f ${SSH_KEY} -q -N ""


# --- Setup Cronjobs -----------------------------------------------

echo "Successfully generated Cron jobs"
echo ""

# --- Postwork -----------------------------------------------------

# storing SSH_KEY in config
echo "HP_SSH_KEY=${SSH_KEY}" >> ${DOTENV}

echo "Honeypot setup is complete."
echo "Please share your public key information immediately with:"
echo "  Max Resing <m.resing-1@student.utwente.nl>"
echo ""
echo "Public Key:"
echo $(cat ${SSH_KEY}.pub)
echo ""
echo "After sharing the key information, you need to reboot the honeypot."
echo "Reboot now? [y/n]"
read do_reboot

if [[ ${do_reboot} == "y" ]] ; then
  reboot
fi

