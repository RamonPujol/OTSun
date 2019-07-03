# Default settings for OTSun. These items must be configured as follows:
# 1. Create a copy of this file wherever you want (say /etc/otsun_config.py)
# 2. Create an environment variable OTSUN_CONFIG_FILE pointing to the file
# 3. Make this environment variable visible to the wsgi process that calls the app
#    (see http://ericplumb.com/blog/passing-apache-environment-variables-to-django-via-mod_wsgi.html)
UPLOAD_FOLDER = '/tmp/OTSunDevelopmentServer'
MAIL_SENDER = 'no@no.com'
MAIL_SERVER = 'smtp.no.com'
MAIL_PASSWD = 'secret'
MAIL_PORT = 0
APP_NAME = 'OTSun Development Server'
