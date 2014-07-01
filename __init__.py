from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mail import Mail




app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {"DB": "bitnotes"}
app.config["SECRET_KEY"] = "KeepThisS3cr3t"

db = MongoEngine(app)

app.debug = True
app.config['DEBUG_TB_PANELS'] = (
    'flask.ext.debugtoolbar.panels.versions.VersionDebugPanel',
    'flask.ext.debugtoolbar.panels.timer.TimerDebugPanel',
    'flask.ext.debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask.ext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flask.ext.debugtoolbar.panels.template.TemplateDebugPanel',
    'flask.ext.debugtoolbar.panels.logger.LoggingPanel',
    'flask.ext.mongoengine.panels.MongoDebugPanel'
)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['DEFAULT_MAIL_SENDER'] = 'info@site.com'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
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
    app.run()
