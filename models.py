import datetime
from flask import url_for
from bitnotes import db
from flask.ext.security import UserMixin, RoleMixin, MongoEngineUserDatastore

class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255, unique=True)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])
    bitbooks = db.ListField(db.ReferenceField('BitBook'))
    mail = db.ReferenceField('BitMail')

user_datastore = MongoEngineUserDatastore(db, User, Role)

class BitMailItem(db.Document):
	bitnote = db.ReferenceField('BitNote')
	bitbook = db.ReferenceField('BitBook')
	from_user = db.ReferenceField('User')
	to_user = db.ReferenceField('User')
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	red = db.BooleanField(required=True, default=False)
	message = db.StringField(max_length=255)

class BitMail(db.Document):
	inbox = db.ListField(db.ReferenceField(BitMailItem, reverse_delete_rule=db.PULL))
	outbox = db.ListField(db.ReferenceField(BitMailItem, reverse_delete_rule=db.PULL))
	trash = db.ListField(db.ReferenceField(BitMailItem, reverse_delete_rule=db.PULL))

class BitField(db.EmbeddedDocument):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	title = db.StringField(max_length=255, required=True)

	def __unicode__(self):
		return self.title

	@property
	def bit_field_type(self):
		return self.__class__.__name__

	meta = {
		'allow_inheritance': True,
		'indexes': ['-created_at', 'title'],
		'ordering': ['title']
		}

class BitNote(db.DynamicDocument):
	owners = db.ListField(db.ReferenceField('User'))
	editors = db.ListField(db.ReferenceField('User'))
	viewers = db.ListField(db.ReferenceField('User'))
	public = db.BooleanField(default=False)
	bitfields = db.ListField(db.EmbeddedDocumentField(BitField))
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	title = db.StringField(max_length=255, required=False)
	meta = {'allow_inheritance':True}

	meta = {
		'indexes': ['-created_at'],
		'ordering': ['-created_at']
	}

	def save_to_bitbook(self, bitbook):
		bitbook.bitnotes.append(self)
		for field in self.bitfields:
			if field.title not in bitbook.cover_fields:
				bitbook.cover_fields[field.title] = field
		bitbook.save()

	def share_to(self, to_user, from_user, msg, access):
		#create mailbox if does not exist:
		fr, to = user_mail_context(from_user, to_user)
		manage_access(self, access, to, fr)
		message = BitMailItem(bitnote=self, from_user=fr, to_user=to, message=msg)
		message.save()
		to.mail.inbox.append(message)
		to.mail.save()
		fr.mail.outbox.append(message)
		fr.mail.save()

class BitBook(db.DynamicDocument):
	owners = db.ListField(db.ReferenceField('User'))
	editors = db.ListField(db.ReferenceField('User'))
	viewers = db.ListField(db.ReferenceField('User'))
	public = db.BooleanField(default=False)
	title = db.StringField(max_length=255, required=True)
	description = db.StringField(required=False)
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	cover_fields = db.DictField(required=False)
	bitnotes = db.ListField(db.ReferenceField(BitNote))
	thumbnail = db.ImageField(size=(800, 600, True), thumbnail_size=(150,150,True))

	def share_to(self, to_user, from_user, msg, access):
		#create mailbox if does not exist:
		fr, to = user_mail_context(from_user, to_user)
		#manage access:
		manage_access(self, access, to, fr)
		message = BitMailItem(bitbook=self, from_user=fr, to_user=to, message=msg)
		message.save()
		to.mail.inbox.append(message)
		to.mail.save()
		fr.mail.outbox.append(message)
		fr.mail.save()



class BlogPost(BitField):
	body = db.StringField(required=False)

class Code(BitField):
	body = db.StringField(required=False)

class Rating(BitField):
	rating_scale = db.IntField(default=5)
	rating_value = db.IntField(default=0)

	@property
	def rating(self):
		if rating_count > 0:
			return self.rating_value/self.rating_scale
		else:
			return 0

class Video(BitField):
	embed_code = db.StringField(required=False)

class Link(BitField):
	link = db.StringField(max_length=255, required=False)

class EmailList(BitField):
	email_list = db.ListField(db.EmailField())

class Number(BitField):
	value = db.DecimalField()

class DataSeries(BitField):
	data_points = db.StringField(default='0')

class Switch(BitField):
	state = db.BooleanField(default=False) 

class Image(BitField):
	image_url = db.StringField(required=False, max_length=255)

class Quote(BitField):
	body = db.StringField(required=False)
	author = db.StringField(verbose_name="Author Name", required=False, max_length=255)

class Comment(db.EmbeddedDocument):
	body = db.StringField(verbose_name="Comment", required=True)
	author = db.ReferenceField('User')

class CommentBox(BitField):
	comments = db.ListField(db.EmbeddedDocumentField('Comment'))
	def __unicode__(self):
		return self.title

class CheckList(BitField):
	items = db.StringField()

#devices
class Device(db.DynamicDocument):
	name = db.StringField(required=True)
	meta = {'allow_inheritance': True,}
	

class Availib(Device):
	avil_from = db.DateTimeField(default=datetime.datetime.now, required=True)
	avail_to = db.DateTimeField(required=False)
	allowed_usrs = db.ListField(db.ReferenceField(User))
	reservations = db.ListField(db.ReferenceField('Reservation'))

class Reservation(db.EmbeddedDocument):
	made_by = db.ReferenceField(User)
	from_time = db.DateTimeField(default=datetime.datetime.now, required=True)
	to_time = db.DateTimeField(required=True)

	def check_avilability(self, fr, to):
		f = Reservation.objects(from_time__lte = fr, to_time = to)

def user_mail_context(from_user, to_user):
		if not from_user.mail:
			m = BitMail().save()
			from_user.mail = m
			from_user.save()
		to, created = User.objects.get_or_create(email=to_user)
		if created:
			to.password = 'temp123'
			
		if not to.mail:
			m = BitMail().save()
			to.mail = m
			to.save()
		fr = from_user
		return fr, to	

def manage_access(obj, access, to, fr):
	if fr in obj.owners:
		#Grant permissions
		if access['o'] == 1 and to not in obj.owners:
			obj.owners.append(to)
		if access['e'] == 1 and to not in obj.editors:
			obj.editors.append(to)
		if access['v'] == 1 and to not in obj.viewers:
			obj.viewers.append(to)
		#!overrides all!
		if access['p'] == 1:
			obj.public = True
		#Revoke permissions
		if access['o'] == 0 and to in obj.owners:
			del obj.owners[obj.owners.index(to)]
		if access['e'] == 0 and to in obj.editors:
			del obj.editors[obj.editors.index(to)]
		if access['v'] == 0 and to in obj.viewers:
			del obj.viewers[obj.viewers.index(to)]
		if access['p'] == 0:
			obj.public = False
		#finally save
		obj.save()



#mocks
# BB = BitBook()
# BN1 = BitNote()
# Q = Quote(title='A quote', body='long body', author='Adam Piotrowski', embedded_in=BN1)
# BN1.bitfields.append(Q)
# P = BlogPost(title='post', body='long post of a blog post')
# #C = Comment(body='asdasd', author=User.objects.all()[0])
# CB = CommentBox(title='commentbox')
# #CB.comments.append(C)
# BN1.bitfields.append(P)
# BN1.bitfields.append(CB)
# U = User.objects.all()[0]

def clean_all_shit():
	BitNote.objects.all().delete()
	BitBook.objects.all().delete()
	User.objects.all().delete()
	BitMail.objects.all().delete()
	BitMailItem.objects.all().delete()
	User(email='a.piotrowski@g.pl', password='pass', confirmed_at=datetime.datetime.now).save()
	print 'ok'


