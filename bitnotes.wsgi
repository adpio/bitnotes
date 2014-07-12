activate_this = '/var/www/bitnotes/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from bitnotes import app as application