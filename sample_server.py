import os
from webappsunscene import app as application

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

# customize the next lines
application.config.from_mapping(
    APP_NAME="OTSunWebApp Testing",
    UPLOAD_FOLDER = get_dir(),
    MAIL_SENDER = None,
    MAIL_USERNAME = None,
    MAIL_SERVER = None,
    MAIL_PASSWD = None,
    MAIL_PORT = None
)

