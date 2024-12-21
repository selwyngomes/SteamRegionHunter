#!/bin/bash

echo "Setting up SteamRegionHunter..."
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Setup complete! Run the app using: python -m steam_region_hunter.main"
