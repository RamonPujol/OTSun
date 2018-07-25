import sys, os
mypath = os.path.dirname(__file__)
sys.path.insert(0, mypath)
# from webappsunscene import app as application

def application(environ, start_response):
    ENVIRONMENT_VARIABLES = [
            'OTSUN_CONFIG_FILE',
        ]
    for key in ENVIRONMENT_VARIABLES:
        os.environ[key] = environ.get(key)

    from webappsunscene import app
    return app(environ, start_response)
    