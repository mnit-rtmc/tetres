#!/bin/bash
#SET SERVER=%~dp0\Server\src\server.py
#read userInput
#echo $userInput
# shellcheck disable=SC2034
_redText=\\e[31m
_greenText=\\e[32m
_yellowText=\\e[33m
_blueText=\\e[34m
_magentaText=\\e[35m
_cyanText=\\e[36m
_whiteText=\\e[37m
_resetText=\\e[0m

_serverPath="./Server/src/server.py"

echo -e "$_cyanText""Starting Server...""$_resetText"
ve/bin/python3 $_serverPath
echo -e "$_cyanText""Done""$_resetText"
