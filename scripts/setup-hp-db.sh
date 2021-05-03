#!/bin/bash

# ------------------------------------------------------------------
#
# Setup script for the central database server which is use to store
# the log data of all honeypots.
#
# Script will set up:
#  * Basic utilities (e.g. curl)
#  * Postgres database server
#
# The script symlinks /mnt/data/postgresql to /var/lib/postgresql to
# ensure the database is stored on the mounted volume.
#
# by Max Resing <m.resing-1@student.utwente.nl>
#
# ------------------------------------------------------------------

SEMAPHORE=honeypotsetup
VERSION=0.1.0
USAGE="Usage: $0 [-d] [-m] [-vh]"

# Flags
setup_misc=false
setup_sql=false

# Constants
PG_DATA=/var/lib/postgresql
MNT_DATA=/mnt/data
DB_NAME=honeypot


# --- Option processing --------------------------------------------
if [ $# == 0 ] ; then
  echo $USAGE
  exit 1;
fi

while getopts "dmvh?" opt; do
  case $opt in
    d)
      setup_sql=true
      ;;
    m)
      setup_misc=true
      ;;
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


if [[ "$setup_misc" = true ]] ; then
  echo "Performing general setup tasks:"

  echo "  * Updating system"
  apt-get -qq update
  apt-get -qq dist-upgrade

  echo "  * Installing common software"
  apt-get -qq install curl wget neovim

  echo "  * Configure .bashrc"
  rm -f $HOME/.bashrc
  curl -s https://codeberg.org/resingm/bashrc/raw/branch/master/bashrc -o /home/$SUDO_USER/.bashrc
  chown $SUDO_USER:$SUDO_USER /home/$SUDO_USER/.bashrc
fi


if [[ "$setup_sql" = true ]] ; then
  echo "Performing Postgres installation:"

  echo "  * Create symlink for mountpoint"

  if [[ -d $PG_DATA ]] ; then
    rm -rf $PG_DATA
  fi

  mkdir -p $MNT_DATA/postgresql
  ln -s $MNT_DATA/postgresql $PG_DATA


  echo "  * Installing Postgres"
  apt-get -qq install postgresql

  echo "  * Enable/Start systemd service unit"
  systemctl -q enable postgresql.service
  systemctl -q start postgresql.service

  echo "  * Setup '$SUDO_USER' as DB user"
  sudo -u postgres createuser --superuser -P $SUDO_USER
  sudo -u $SUDO_USER createdb $DB_NAME

  echo "  * Configure postgresql"
  echo "listen_addresses = '127.0.0.1'" >> /etc/postgresql/postgresql.conf

  echo "  * Configure pg_hba.conf"
  echo "host    all   $SUDO_USER    127.0.0.1/32    md5" >> /etc/postgresql/pg_hba.conf

fi
