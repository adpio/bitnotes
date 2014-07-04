from flask.ext.mail import Message
from flask import url_for, flash, current_app, request, session, render_template

def send_mail(subject, recipient, sender, template, context):
	context['sender'] = sender
	context['recipient'] = recipient
	msg = Message(subject, sender=sender, recipients=[recipient])
	ctx = ('email', template)
	msg.body = render_template('%s/%s.txt' % ctx, **context)
	msg.html = render_template('%s/%s.html' % ctx, **context)
	mail = current_app.extensions.get('mail')
	mail.send(msg)