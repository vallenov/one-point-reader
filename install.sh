#!/bin/bash

echo Install One-point Reader...

WORK_DIR=`pwd`

sudo apt install python
sudo apt install pip

if [[ `ls requirements.txt` != "" ]]
    then
        python -m venv .venv
    fi
. .venv/bin/activate && echo activate venv
pip install -r requirements.txt

echo -e "[Desktop Entry]
Type=Application
Name=One-point Reader
GenericName=One-point Reader
Comment=Application
Exec=$WORK_DIR/start.sh
TryExec=$WORK_DIR/start.sh
Terminal=false
Icon=$WORK_DIR/icon.png
Categories=Graphics
StartupNotify=true" | sudo tee /usr/share/applications/one-point-reader.desktop

echo -e "cd $WORK_DIR
. .venv/bin/activate
nohup .venv/bin/python one-point-reader.py &" | sudo tee $WORK_DIR/start.sh

echo "Install is done"