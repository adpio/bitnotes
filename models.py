import datetime
from flask import url_for
from bitnotes import db
from flask.ext.security import UserMixin, RoleMixin, MongoEngineUserDatastore



class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])
    bitbooks = db.ListField(db.ReferenceField('BitBook'))

user_datastore = MongoEngineUserDatastore(db, User, Role)


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
	meta = {'allow_inheritance':True}

	def save_to_bitbook(self, bitbook):
		bitbook.bitnotes.append(self)
		for field in self.bitfields:
			if field.title not in bitbook.cover_fields:
				bitbook.cover_fields[field.title] = field
		bitbook.save()



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
P = BlogPost(title='post', body='long post of a sexy blog post')
#C = Comment(body='asdasd', author=User.objects.all()[0])
CB = CommentBox(title='commentbox')
#CB.comments.append(C)
BN1.bitfields.append(P)
BN1.bitfields.append(CB)


def clean_all_shit():
	BitNote.objects.all().delete()
	BitBook.objects.all().delete()
	print 'ok'


