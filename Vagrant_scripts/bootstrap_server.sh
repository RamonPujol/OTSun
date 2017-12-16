#!/usr/bin/env bash

cp /vagrant/server_files/mysites.conf /etc/apache2/sites-available/
chmod 644 /etc/apache2/sites-available/mysites.conf
a2ensite mysites
a2dissite 000-default
service apache2 reload
echo "-------------------------------------------------"
echo "| ServerName and home location must be verified |"
echo "-------------------------------------------------"
