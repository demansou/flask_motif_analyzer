activate_this = '/var/www/flask_app/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from motif_analyzer import app

import sys

sys.stdout = sys.stderr
