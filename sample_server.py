from webappsunscene import app as application
# customize the next lines
application.config.from_mapping(
    APP_NAME="OTSunWebApp Development",
    UPLOAD_FOLDER = '/tmp/OTSunDevelopmentServer',
    MAIL_SENDER = None,
    MAIL_SERVER = None,
    MAIL_PASSWD = None,
    MAIL_PORT = None
)
