import sys, os
mypath = os.path.dirname(__file__)
sys.path.insert(0, mypath)
# from webappsunscene import app as application
import logging

def application(environ, start_response):
    ENVIRONMENT_VARIABLES = [
            'OTSUN_CONFIG_FILE',
        ]
    for key in ENVIRONMENT_VARIABLES:
        os.environ[key] = environ.get(key)

    from webappsunscene import app

    logfile = os.path.join(app.config['UPLOAD_FOLDER'],'logging.log')
    handler = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    return app(environ, start_response)
