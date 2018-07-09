#!/bin/sh

sudo chmod 777 /dev/ttyUSB0
sudo mkdir -p -m 777 /var/run/uwsgi
sudo chown friday:friday /var/run/uwsgi
sudo mkdir -p -m 777 /var/log/uwsgi
sudo chown friday:friday /var/log/uwsgi

sudo systemctl start uwsgi-robot.service
