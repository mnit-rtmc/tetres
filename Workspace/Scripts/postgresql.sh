#!/bin/bash
#SET SERVER=%~dp0\Server\src\server.py
#read userInput
#echo $userInput
#sudo -u postgres psql
#systemctl is-active postgresql
#/var/lib/postgresql/11/main
#sudo systemctl stop postgresql
#sudo rsync -av /var/lib/postgresql ./data/

#stop service:
#   systemctl stop postgresql
#start service:
#   systemctl start postgresql
#show status of service:
#   systemctl status postgresql
#disable service(not auto-start any more)
#   systemctl disable postgresql
#enable service postgresql(auto-start)
#   systemctl enable postgresql

# sudo apt-get remove synaptic*
# sudo apt-get purge synaptic*
# sudo apt-get autoremove
# sudo apt-get autoclean

# Start a screen
#   $ screen
#   Then run any commands
# Detach from screen
#   $ CTRL+A release then D
# List all screens
#   $ screen -list
# Attach to screen
#     $ screen -r
#   or
#     $ screen -r name_0f_screen
# Kill screen
#   $ CTRL+D

# shellcheck disable=SC2034
_redText=\\e[31m
_greenText=\\e[32m
_yellowText=\\e[33m
_blueText=\\e[34m
_magentaText=\\e[35m
_cyanText=\\e[36m
_whiteText=\\e[37m
_resetText=\\e[0m

isRunning() {
  echo -e "$_magentaText""Is PostgreSQL Running?""$_resetText"
  systemctl is-active postgresql
}

echo -e "$_cyanText""Running Start_PostgreSQL Script...""$_resetText"

isRunning

echo -e "$_cyanText""Starting PostgreSQL...""$_resetText"
systemctl start postgresql

isRunning

echo -e "$_cyanText""Type \q To Quit And Shutdown PostgreSQL""$_resetText"
sudo -u postgres psql

echo -e "$_cyanText""Stopping PostgreSQL...""$_resetText"
systemctl stop postgresql

isRunning

echo -e "$_cyanText""Done""$_resetText"
