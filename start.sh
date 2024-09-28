#!/bin/bash
python3 -m venv venv
source venv/bin/activate
fastapi dev main.py
