#/bin/bash

# another terminal

# gunicorn --bind 127.0.0.1:6000 slave:app &
# gunicorn --bind 127.0.0.1:6001 slave:app &
# gunicorn --bind 127.0.0.1:6002 slave:app &
# gunicorn --bind 127.0.0.1:5000 worker:app &
# gunicorn --bind 127.0.0.1:5001 worker:app &
# # don't run act_as_online_database with gunicorn because if you do then when you make changes in act_as_online database it's not update
# gnome-terminal --command="python3 act_as_online_database.py" &
# gunicorn --bind 127.0.0.1:7001 master:app;


echo "killing gunicorn"
pkill gunicorn;
echo "killing python3"
pkill python3;


# Use of ; No matter the first command cmd1 run successfully or not, always run the second command cmd2:
# virtual environment https://linuxize.com/post/how-to-create-python-virtual-environments-on-ubuntu-18-04/
# multiple terminal https://dev.to/gauravpurswani/how-to-execute-commands-from-another-terminals-by-being-on-just-one-terminal-1550

gunicorn --bind 127.0.0.1:6000 slave:app &
gunicorn --bind 127.0.0.1:6001 slave:app &
gunicorn --bind 127.0.0.1:6002 slave:app &
gunicorn --bind 127.0.0.1:5000 worker:app &
gunicorn --bind 127.0.0.1:5001 worker:app &
# don't run act_as_online_database with gunicorn because if you do then when you make changes in act_as_online database it's not update
python3 act_as_online_database.py &
gunicorn --bind 127.0.0.1:7001 master:app;
