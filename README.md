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
If you want to send mail you have to create config for flask-mail. Create "config" folder in the project dir and 2 files: __init__.py and email.py.
Edit email.py to:
```python
MAIL_SERVER : default ‘localhost’
MAIL_PORT : default 25
MAIL_USE_TLS : default False
MAIL_USE_SSL : default False
MAIL_DEBUG : default app.debug
MAIL_USERNAME : default None
MAIL_PASSWORD : default None
MAIL_DEFAULT_SENDER : default None
MAIL_MAX_EMAILS : default None
MAIL_SUPPRESS_SEND : default app.testing
```
Leave __init__.py empty.