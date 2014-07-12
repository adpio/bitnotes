BitNotes
========
#What the fuck is that?
BitNotes is the new way of storing, sending and sharing information.
#Installation
##Use linux:
python-dev is required for PIL installation so:
```sh
sudo apt-get install python-dev
```

##Install requirements:
```sh
pip install -r reqirements.txt
```
##After successful installation you can run test server with:
```sh
python manage.py runserver
```
##Extra config
If you want to send mail you have to create config for flask-mail. Create "config" folder in the project dir and 2 files: \_\_init\_\_.py security.py and email.py.
Edit email.py to:
```python
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'username@gmail.com'
MAIL_PASSWORD = 'password'
```
Edit security.py to:
```python
app.debug = True
app.config["MONGODB_SETTINGS"] = {"DB": "bitnotes"}
app.config["SECRET_KEY"] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['DEFAULT_MAIL_SENDER'] = 'postman@bitnotes.com'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
```
Leave __init__.py empty.