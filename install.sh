#!/bin/bash

echo "====================================="
echo "KoemojiAuto Installer"
echo "====================================="
echo

# Pythonの確認
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo
    echo "Please install Python 3.9 or later:"
    echo
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  brew install python3"
    else
        echo "  sudo apt install python3 python3-pip"
    fi
    echo
    exit 1
fi

echo "Python is installed."
echo

# pipの確認と更新
echo "Updating pip..."
python3 -m pip install --upgrade pip >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[WARNING] Failed to update pip. Continuing..."
fi

# インストーラ実行
echo "Starting dependency installer..."
echo
python3 install_dependencies.py

echo
echo "====================================="
echo "Installation process completed."
echo "====================================="
echo
echo "To start KoemojiAuto, run:"
echo "  ./tui.sh"
echo