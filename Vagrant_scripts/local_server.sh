#!/usr/bin/env bash

# add-apt-repository -y ppa:freecad-maintainers/freecad-stable
apt update
apt -y install python-pip
git clone https://github.com/bielcardona/OTSun.git
apt -y install freecad
pip install -e OTSun/
pip install -e /vagrant/

