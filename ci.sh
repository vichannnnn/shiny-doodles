#!/bin/bash

tmux attach-session -t shiny-dev
source venv/bin/activate
pip install -r requirements.txt
python main.py
