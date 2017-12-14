#!/usr/bin/env bash

add-apt-repository -y ppa:freecad-maintainers/freecad-stable 
apt-get update
apt-get install -y freecad
apt-get install -y python-numpy
apt-get install -y python-enum
apt-get install -y python-pip
apt-get install -y apache2 
apt-get install -y libapache2-mod-wsgi
pip install virtualenv
