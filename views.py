from flask import Blueprint, request, redirect, render_template, url_for, flash
from flask.views import MethodView
import json
from flask.ext.mongoengine.wtf import model_form
# from flask.ext.mongoengine.wtf.fields import *
# from flask.ext.mongoengine.wtf.model import Form
from bitnotes.models import *
from flask.ext.security import login_required
from flask_login import current_user
from utils import send_mail
#forms
from wtforms import Form
from wtforms import TextField, BooleanField, HiddenField, TextField, TextAreaField
from wtforms.validators import DataRequired, Email
import opengraph
from geopy.geocoders import Nominatim


posts = Blueprint('posts', __name__, template_folder='templates')


class SendBitBookForm(Form):
	to_user = TextField('email', validators=[Email()])
	message = TextField('message', validators=[DataRequired()])
	o = BooleanField('o')
	e = BooleanField('e')
	v = BooleanField('v')
	p = BooleanField('p')

class Mailer(MethodView):
	@login_required
	def post(self):
		from_user = User.objects.get_or_404(id=current_user.id)
		to_user = request.form['to_user']
		msg = request.form['msg']
		access = {}
		for x in ['o','e','v','p']:
			if x not in request.form:
				access[x]=0
			else:
				access[x]=1
		if 'note_id' in request.form:
			note_id = request.form['note_id']
			note = BitNote.objects.get_or_404(id=note_id)
			#TODO: security
			note.share_to(to_user=to_user, from_user=from_user, msg=msg, access=access)
			mail_ctx = {'subject':'BitNote from %s'%from_user.email,
						'sender' : from_user.email,
						'recipient': to_user,
						'template': 'note',
						'context': {'note':note},
						}
			send_mail(**mail_ctx)
			return json.dumps({'ok':True})

		elif 'bitbook_id' in request.form:
			bitbook = BitBook.objects.get_or_404(id=request.form['bitbook_id'])
			bitbook.share_to(to_user=to_user, from_user=from_user, msg=msg, access=access)
			mail_ctx = {'subject':'BitBook from %s'%from_user.email,
						'sender' : from_user.email,
						'recipient': to_user,
						'template': 'bitbook',
						'context': {'bitbook':bitbook},    
			}
			send_mail(**mail_ctx)
			return json.dumps({'ok':True})
		else:
			return json.dumps({'ok':False})

class MailBox(MethodView):
	@login_required
	def get(self, folder='inbox'):
		active = folder
		user = User.objects.get_or_404(id=current_user.id)
		if not user.mail:
			mail = BitMail().save()
			user.mail = mail
			user.save()
		m = user.mail
		mail_count = {
			'inbox': len(m.inbox),
			'outbox': len(m.outbox),
			'trash': len(m.trash),
		}
		if folder == 'inbox':
			folder = m.inbox
		elif folder == 'outbox':
			folder = m.outbox
		else:
			folder = m.trash
		#TODO: security
		if request.args != {} and request.args['active_item']:
			active_item_id = request.args['active_item']
			active_item = BitMailItem.objects.get_or_404(id=active_item_id)
		else:
			active_item = None
		return render_template('mailbox.html', user=user, folder=folder, active=active, mail_count=mail_count, active_item=active_item)

class MailHandler(MethodView):
	@login_required
	def get(self, folder, bitmail_id, action):
		#get context
		user = User.objects.get_or_404(id=current_user.id)
		bitmail = BitMailItem.objects.get_or_404(id=bitmail_id)

		if action == 'destroy':
			bitmail.delete()
			flash(u'Destroyed', 'danger')
		if action == 'trashit' and folder in ['inbox', 'outbox']:
			folder = user.mail[folder]
			del(folder[folder.index(bitmail)])
			user.mail.trash.append(bitmail)
			user.mail.save()
			flash(u'Trashed', 'warning')
		if action == 'add_to_bit_books':
			if bitmail.bitbook in user.bitbooks:
				flash(u'Already in your BitBooks', 'warning')
			else:
				user.bitbooks.append(bitmail.bitbook)
				user.save()
				flash(u'Added', 'success')
		if action == 'create_bitbook_from_note':
			note = bitmail.bitnote
			B = BitBook(title='Enter BitBook Title', description='Add some description')
			B.save()
			note.save_to_bitbook(bitbook=B)
			user.bitbooks.append(B)
			user.save()
			flash(u'Created', 'success')
		if action == 'add_note_to_bitbook':
			B = BitBook.objects.get_or_404(id=request.args['b_id'])
			note = bitmail.bitnote
			note.save_to_bitbook(bitbook=B)
			flash(u'Added', 'success')
		return redirect(url_for('posts.mail', folder=folder))

class BitBookShelf(MethodView):
	form = model_form(BitBook, exclude=['created_at','cover_fields','bitnotes','owners','editors','viewers'])
	mail_form = SendBitBookForm()
	def get_context(self):
		user = User.objects.get_or_404(id=current_user.id)
		context = {
			'form': self.form(request.form),
			'bitbooks': user.bitbooks,
			'user' : user,
			'mail_form': self.mail_form,
		}
		return context

	@login_required
	def get(self):
		context = self.get_context()
		context['bit_pub'] = BitBook.objects(public=True)[:4]
		return render_template('bookshelf.html', **context)

	@login_required
	def post(self):
		context = self.get_context()
		form = context.get('form')
		user = context.get('user')
		if form.validate():
			b = BitBook()
			form.populate_obj(b)
			b.owners.append(user)
			b.save()
			user.bitbooks.append(b)
			user.save()
			return redirect(url_for('posts.bitbook', bitbook_id=b.id))
		return render_template('bookshelf.html', **context)
	
class BitBookView(MethodView):
	@login_required
	def get(self, bitbook_id):
		bitbook = BitBook.objects.get_or_404(id=bitbook_id)
		if request.args != {} and request.args['active']:
			active = request.args['active']
			#TODO: security
			a = BitNote.objects.get_or_404(id=active)
		elif bitbook.bitnotes:
			a = bitbook.bitnotes[-1]
		else:
			a = None
		return render_template('bitbook.html', bitbook=bitbook, active=a)
	@login_required
	def post(self, bitbook_id):
		bb = BitBook.objects.get_or_404(id=bitbook_id)
		t = request.form['title']
		d = request.form['description']
		bb.title = t
		bb.description = d
		bb.save()
		return redirect(url_for('posts.bitbook', bitbook_id=bb.id))

	@login_required
	def delete(self, bitbook_id):
		bitbook = BitBook.objects.get_or_404(id=bitbook_id)
		bitbook.delete()
		flash(u'BitBook deleted', 'danger')
		return redirect(url_for('posts.bitbooks'))

	@login_required
	def put(self, bitbook_id):
		bitbook = BitBook.objects.get_or_404(id=bitbook_id)
		note = BitNote()
		#note.bitfields.append(bitbook.cover_fields.values())
		note.save()
		bitbook.bitnotes.append(note)
		bitbook.save()
		return '/%s/%s'%(bitbook.id, note.id)

class BitNoteView(MethodView):

	def get_context(self, bitbook_id, bitnote_id):
		note = BitNote.objects.get_or_404(id=bitnote_id)
		bitbook = BitBook.objects.get_or_404(id=bitbook_id)       
		unused_bitfields = bitbook.cover_fields
		for field in note.bitfields:
			if field.title in unused_bitfields:
				unused_bitfields.pop(field.title)
		unused_bitfields = unused_bitfields.values()
		return note, bitbook, unused_bitfields
	
	def get(self, bitbook_id, bitnote_id):
		note, bitbook, unused_bitfields = self.get_context(bitbook_id, bitnote_id)
		return render_template('notes/note.html', note=note, bitbook=bitbook, unused_bitfields=unused_bitfields)

	@login_required
	def post(self, bitbook_id, bitnote_id):
		note, bitbook, unused_bitfields = self.get_context(bitbook_id, bitnote_id)
		field_type = request.form['field_type']
		field_title = request.form['field_title']
		if field_type == 'Heading':
			h = request.form['Heading']
			note.title = h
			note.save()
		else:
			field = [x for x in note.bitfields if x.title == field_title][0]
			if field:
				if field_type == 'CommentBox':
					body = request.form['body']
					author = User.objects.get_or_404(id=current_user.id)
					#author = User().save()
					c = Comment(body=body, author=author)
					field.comments.append(c)
				elif field_type == 'Link':
					if request.form['link']:
						link = request.form['link']
						field.link = link
						l = opengraph.OpenGraph(url=link)
						if l.is_valid():
							field.og_url = l.url
							field.og_title = l.title
							field.og_type = l.type
							field.og_image = l.image
							if 'description' in l.keys():
								field.og_description = l.description
				elif field_type == 'Location':
					geolocator = Nominatim()
					a = request.form['address']
					l = geolocator.geocode(a)
					field.location = [l.latitude, l.longitude]
					field.addr = l.address
				else:
					constructor = globals()[field_type]
					mform = model_form(constructor, exclude=['created_at','title'])
					form = mform(request.form)
					form.populate_obj(field)
				note.save()

		return render_template('notes/note.html', note=note, bitbook=bitbook, unused_bitfields=unused_bitfields)

	@login_required
	def delete(self, bitbook_id, bitnote_id):
		note = BitNote.objects.get_or_404(id=bitnote_id)
		note.delete()
		flash(u'BitNote deleted', 'danger')
		return '/%s/%s'%(bitbook.id)


class FieldManager(MethodView):
	def post(self, bitnote_id, bitbook_id):
		#TODO security
		note = BitNote.objects.get_or_404(id=bitnote_id)
		bitbook = BitBook.objects.get_or_404(id=bitbook_id)

		field_type = request.form['field_type']
		field_title = request.form['field_title']
		task = request.form['task']
		
		if task == 'create':
			if (not[ x for x in note.bitfields if x.title == field_title]) and (field_title not in bitbook.cover_fields):
				#constructing class from string:
				constructor = globals()[field_type]
				new_field = constructor(title=field_title)
				#adding field to note:
				note.bitfields.append(new_field)
				note.save()
				bitbook.cover_fields[field_title] = new_field
				bitbook.save()
					
		if task == 'delete':
			note.update(pull__bitfields__title=field_title)
			note.save()
			# if not BitBook.objects(id=bitbook.id, bitnotes__bitfields__title=field_title):
			#     del bitbook.cover_fields[field_title]
			#     bitbook.save()



		if task == 'update':
			if (not[ x for x in note.bitfields if x.title == field_title]) and (field_title in bitbook.cover_fields):
				note.bitfields.append(bitbook.cover_fields[field_title])
				note.save()

		return redirect(url_for('posts.bitnote', bitbook_id=bitbook_id, bitnote_id = note.id))


@posts.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html')

# Register the urls
posts.add_url_rule('/<bitbook_id>/', view_func=BitBookView.as_view('bitbook'))
posts.add_url_rule('/<bitbook_id>/<bitnote_id>/field_manager',view_func=FieldManager.as_view('field_manager'))
posts.add_url_rule('/', view_func=BitBookShelf.as_view('bitbooks'))
posts.add_url_rule('/<bitbook_id>/<bitnote_id>/', view_func=BitNoteView.as_view('bitnote'))
posts.add_url_rule('/mailer/', view_func=Mailer.as_view('mailer'))
posts.add_url_rule('/mail/<folder>/', view_func=MailBox.as_view('mail'))
posts.add_url_rule('/mail/<folder>/<bitmail_id>/<action>', view_func=MailHandler.as_view('mail_handler'))


