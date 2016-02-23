from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mail import Mail
from bitnotes.extensions import *
#utf8 workaround
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

app = Flask(__name__)

from config.debug import debugging
app.debug = debugging

#import security conf
app.config.from_object('config.security')

db = MongoEngine(app)

app.config['DEBUG_TB_PANELS'] = (
    'flask.ext.debugtoolbar.panels.versions.VersionDebugPanel',
    'flask.ext.debugtoolbar.panels.timer.TimerDebugPanel',
    'flask.ext.debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask.ext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flask.ext.debugtoolbar.panels.template.TemplateDebugPanel',
    'flask.ext.debugtoolbar.panels.logger.LoggingPanel',
    'flask.ext.mongoengine.panels.MongoDebugPanel'
)

app.config.from_object('config.email')

#Setup mail extension
mail = Mail(app)

from models import user_datastore
from flask.ext.security import Security
security = Security(app, user_datastore)

def register_blueprints(app):
    # Prevents circular imports
    from bitnotes.views import posts
    app.register_blueprint(posts)

register_blueprints(app)
DebugToolbarExtension(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
