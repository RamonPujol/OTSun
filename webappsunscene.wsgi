import sys, os
mypath = os.path.dirname(__file__)
sys.path.insert(0, mypath)
from webappsunscene.server import app as application
