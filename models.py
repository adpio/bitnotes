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

class BitMail(db.Document):
	inbox = db.ListField(db.EmbeddedDocumentField('BitMailItem'))
	outbox = db.ListField(db.EmbeddedDocumentField('BitMailItem'))
	trash = db.ListField(db.EmbeddedDocumentField('BitMailItem'))

class BitMailItem(db.EmbeddedDocument):
	bitnote = db.ReferenceField('BitNote')
	bitbook = db.ReferenceField('BitBook')
	from_user = db.ReferenceField('User')
	to_user = db.ReferenceField('User')
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	red = db.BooleanField(required=True, default=False)
	message = db.StringField(max_length=255)

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
	bitfields = db.ListField(db.EmbeddedDocumentField(BitField))
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	title = db.StringField(max_length=255, required=False)
	meta = {'allow_inheritance':True}

	def save_to_bitbook(self, bitbook):
		bitbook.bitnotes.append(self)
		for field in self.bitfields:
			if field.title not in bitbook.cover_fields:
				bitbook.cover_fields[field.title] = field
		bitbook.save()

	def send_to(self, to_user, from_user, msg):
		#create mailbox if does not exist:
		if not from_user.mail:
			m = BitMail().save()
			from_user.mail = m
			from_user.save()
		to, created = User.objects.get_or_create(email=to_user)
		if created:
			#TODO: send invite here
			pass
		if not to.mail:
			m = BitMail().save()
			to.mail = m
			to.save()	
		message = BitMailItem(bitnote=self, from_user=from_user, to_user=to, message=msg)
		to.mail.inbox.append(message)
		to.mail.save()
		from_user.mail.outbox.append(message)
		from_user.mail.save()

class BitBook(db.DynamicDocument):
	title = db.StringField(max_length=255, required=True)
	description = db.StringField(required=False)
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	cover_fields = db.DictField(required=False)
	bitnotes = db.ListField(db.ReferenceField(BitNote))
	thumbnail = db.ImageField(size=(800, 600, True), thumbnail_size=(150,150,True))

# class Post(db.DynamicDocument):
# 	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
# 	title = db.StringField(max_length=255, required=True)
# 	slug = db.StringField(max_length=255, required=True)
# 	comments = db.ListField(db.EmbeddedDocumentField('Comment'))

# 	def get_absolute_url(self):
# 		return url_for('post', kwargs={"slug": self.slug})

# 	def __unicode__(self):
# 		return self.title

# 	@property
# 	def post_type(self):
# 		return self.__class__.__name__

# 	meta = {
# 		'allow_inheritance': True,
# 		'indexes': ['-created_at', 'slug'],
# 		'ordering': ['-created_at']
# 	}

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
	embed_code = db.StringField(required=True)

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

#mocks
BB = BitBook()
BN1 = BitNote()
Q = Quote(title='A quote', body='long body', author='Adam Piotrowski', embedded_in=BN1)
BN1.bitfields.append(Q)
P = BlogPost(title='post', body='long post of a blog post')
#C = Comment(body='asdasd', author=User.objects.all()[0])
CB = CommentBox(title='commentbox')
#CB.comments.append(C)
BN1.bitfields.append(P)
BN1.bitfields.append(CB)
U = User.objects.all()[0]

def clean_all_shit():
	BitNote.objects.all().delete()
	BitBook.objects.all().delete()
	print 'ok'


