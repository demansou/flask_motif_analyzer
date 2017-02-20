activate_this = '/var/www/flask_app/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
sys.stdout = sys.stderr

import os os.environ['PYTHON_EGG_CACHE'] = '~/tmp/python-eggs'

from motif_analyzer import app


