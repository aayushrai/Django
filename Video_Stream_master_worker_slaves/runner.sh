#/bin/bash

gunicorn --bind 127.0.0.1:5000 worker:app &
gunicorn --bind 127.0.0.1:5001 worker:app &
gunicorn --bind 127.0.0.1:6000 slave:app &
gunicorn --bind 127.0.0.1:6001 slave:app &
gunicorn --bind 127.0.0.1:6002 slave:app &
# don't run act_as_online_database with gunicorn
python3 act_as_online_database.py &
gunicorn --bind 127.0.0.1:7001 master:app 

pkill gunicorn
pkill python3
# python3 worker1.py & 
# python3 slave1.py & 
# python3 slave2.py & 
# python3 master.py

# export FLASK_APP=worker1.py
# flask run --host 0.0.0.0 --port 5000

# export FLASK_APP=worker1.py
# flask run --host 0.0.0.0 --port 6000


# to kill python3 process
#  pkill -9 python3