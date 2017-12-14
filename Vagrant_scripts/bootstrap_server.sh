#!/usr/bin/env bash

cp /vagrant/server_files/mysites.conf /etc/apache2/sites-available/
a2ensite mysites
service apache2 reload
echo "-------------------------------------------------"
echo "| ServerName and home location must be verified |"
echo "-------------------------------------------------"
