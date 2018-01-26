#!/usr/bin/env bash

cd $HOME
if [ -d "webappsunscene" ]; then
  # Control will enter here if $DIRECTORY exists.
  rm -rf webappsunscene
fi
mkdir webappsunscene
cd webappsunscene
cp -r /vagrant/*py ./
cp -r /vagrant/*wsgi ./
cp -r /vagrant/templates ./
cp -r /vagrant/experiments ./
cp -r /vagrant/processors ./
cp -r /vagrant/utils ./
virtualenv venv
source venv/bin/activate
which python
pip install flask
pip install pysunscene
pip install enum
deactivate

