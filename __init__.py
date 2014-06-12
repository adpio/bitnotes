from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {"DB": "my_tumble_log"}
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



def register_blueprints(app):
    # Prevents circular imports
    from bitnotes.views import posts
    from bitnotes.admin import admin
    app.register_blueprint(posts)
    app.register_blueprint(admin)

register_blueprints(app)
DebugToolbarExtension(app)

if __name__ == '__main__':
    app.run()
