#!/bin/bash
source venv/faceRecog/bin/activate


gunicorn --bind 127.0.0.1:6000 slave:app &
gunicorn --bind 127.0.0.1:6001 slave:app &
gunicorn --bind 127.0.0.1:6002 slave:app 