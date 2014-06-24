import datetime
from flask import url_for
from bitnotes import db

# class User(db.Document):
# 	email = db.EmailField(required=True, primary_key=True, help_text='Email is your ID')
# 	#TODO
# 	password = db.StringField(max_length=50, min_length=2)
# 	bitbooks = db.ListField(db.ReferenceField(BitBook))

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



class Cover(BitNote):
	public = db.BooleanField(default=False,required=True)

class BitBook(db.DynamicDocument):
	title = db.StringField(max_length=255, required=True)
	description = db.StringField(required=False)
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	cover_fields = db.DictField(required=False)
	bitnotes = db.ListField(db.GenericReferenceField())
	thumbnail = db.ImageField(size=(800, 600, True), thumbnail_size=(150,150,True))



class Post(db.DynamicDocument):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	title = db.StringField(max_length=255, required=True)
	slug = db.StringField(max_length=255, required=True)
	comments = db.ListField(db.EmbeddedDocumentField('Comment'))

	def get_absolute_url(self):
		return url_for('post', kwargs={"slug": self.slug})

	def __unicode__(self):
		return self.title

	@property
	def post_type(self):
		return self.__class__.__name__

	meta = {
		'allow_inheritance': True,
		'indexes': ['-created_at', 'slug'],
		'ordering': ['-created_at']
	}

class BlogPost(BitField):
	body = db.StringField(required=False)

class Code(BitField):
	body = db.StringField(required=False)

class Rating(BitField):
	rating_scale = db.IntField(default=0)
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
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	body = db.StringField(verbose_name="Comment", required=True)
	author = db.StringField(verbose_name="Name", max_length=255, required=True)

#mocks
BB = BitBook()
BN1 = BitNote()
Q = Quote(title='A quote', body='long body', author='Adam Piotrowski', embedded_in=BN1)
BN1.bitfields.append(Q)
P = BlogPost(title='post', body='long post of a sexy blog post')
BN1.bitfields.append(P)


