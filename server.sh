#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd $DIR

_redText=\\e[31m
_greenText=\\e[32m
_yellowText=\\e[33m
_blueText=\\e[34m
_magentaText=\\e[35m
_cyanText=\\e[36m
_whiteText=\\e[37m
_resetText=\\e[0m

_serverPath="Server/src/server.py"


# If this doesn't work, add sudo back in:

echo -e "$_cyanText""Starting Server...""$_resetText"
ve/bin/python3 $_serverPath
echo -e "$_cyanText""Done""$_resetText"

