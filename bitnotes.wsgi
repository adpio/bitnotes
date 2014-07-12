activate_this = '/var/www/bitnotes/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#sys.path.append('/var/www')
sys.path.append('/var/www/bitnotes')

from bitnotes import app as application
if __name__ == '__main__':
    application.run()