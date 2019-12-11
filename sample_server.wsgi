import os
from webappsunscene import app as application
import logging

def get_dir():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dir = os.path.join(this_dir,'computations')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    else:
        if not os.access(upload_dir, os.W_OK):
            upload_dir += str(uuid4())
            os.makedirs(upload_dir)
    return upload_dir

def get_file():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir,'webapp.log')
    return filename

# customize the next lines
application.config.from_mapping(
    APP_NAME="OTSunWebApp Test",
    UPLOAD_FOLDER = get_dir(),
    MAIL_SENDER = "XXXXXX",
    MAIL_USERNAME = 'XXXXXX',
    MAIL_SERVER = None,
    MAIL_PASSWD = 'XXXXX',
    MAIL_PORT = 587
)

file_handler = logging.FileHandler(get_file())
file_handler.setLevel(logging.DEBUG)

application.logger.setLevel(logging.DEBUG)
application.logger.addHandler(file_handler)
