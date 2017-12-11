#!/usr/bin/env bash

cd $HOME
mkdir webappsunscene
cd webappsunscene
cp -r /vagrant/*py ./
cp -r /vagrant/*wsgi ./
cp -r /vagrant/templates ./
virtualenv venv
source venv/bin/activate
which python
pip install flask
deactivate
