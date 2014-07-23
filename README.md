BitNotes
========
#What the f is that?
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
If you want to send mail you have to create config for flask-mail. Create "config" folder in the project dir and 4 files: 
- \_\_init\_\_.py 
- security.py 
- email.py
- debug.py

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
MONGODB_SETTINGS = {"DB": "bitnotes"}
SECRET_KEY = "secrest_key"
DEBUG_TB_INTERCEPT_REDIRECTS = False
DEFAULT_MAIL_SENDER = 'postman@bitnotes.com'
SECURITY_REGISTERABLE = True
SECURITY_CONFIRMABLE = True
SECURITY_RECOVERABLE = True
```
Edit debug.py to:
```python
debugging = True
```
Leave \_\_init\_\_.py empty.
#Run
It's a flask app so:
```sh
python manage.py runserver
```