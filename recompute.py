#
# This file must be put in the root folder of the server
# (this folder contains de folder 'computations')
#
from webappsunscene import run_offline, app
import os
import sys

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

if __name__ == '__main__':
    folder = get_dir()
    ident = sys.argv[1]
    app.config.from_mapping(UPLOAD_FOLDER = folder)
    run_offline(ident)
