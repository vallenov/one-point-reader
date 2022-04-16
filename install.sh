#!/bin/bash

echo Install One-point Reader...

WORK_DIR=`pwd`

sudo apt install python3
sudo apt install python3-pip

if [ ! -d "$WORK_DIR/.venv" ]
    then
        echo Create venv
        python -m venv .venv
    fi
. .venv/bin/activate && echo activate venv
pip install -r requirements.txt

# Генерация файла запуска
echo -e "cd $WORK_DIR
. .venv/bin/activate
nohup .venv/bin/python one-point-reader.py &" | sudo tee $WORK_DIR/start.sh
sudo chmod 755 $WORK_DIR/start.sh

# Генерация файла деинсталяции
echo -e "cd $WORK_DIR
sudo rm -rf /usr/share/applications/one-point-reader.desktop
sudo rm -rf $WORK_DIR/.venv
sudo rm -rf $WORK_DIR/start.sh
sudo rm -rf $WORK_DIR/uninstall.sh
echo Uninstall complete" | sudo tee $WORK_DIR/uninstall.sh
sudo chmod 755 $WORK_DIR/uninstall.sh

# Генерация ярлыка запуска
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

echo "Install is done"