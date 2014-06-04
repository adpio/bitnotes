import datetime
from flask import url_for
from bitnotes import db




class BitBook(db.DynamicDocument):
	bitnotes = db.ListField(db.GenericEmbeddedDocumentField())


class BitNote(db.EmbeddedDocument):
    bitfields = db.ListField(db.GenericEmbeddedDocumentField())
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    meta = {'allow_inheritance':True}

class Cover(BitNote):
	public = db.BooleanField(default=False,required=True)

class BitField(db.EmbeddedDocument):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	title = db.StringField(max_length=255, required=True)
	def get_absolute_url(self):
		return url_for('post', kwargs={"slug": self.slug})

	def __unicode__(self):
		return self.title

	@property
	def post_type(self):
		return self.__class__.__name__

	meta = {
	    'allow_inheritance': True,
		'indexes': ['-created_at', 'title'],
		'ordering': ['title']
		}



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
	body = db.StringField(required=True)


class Video(BitField):
	embed_code = db.StringField(required=True)


class Image(BitField):
	image_url = db.StringField(required=True, max_length=255)


class Quote(BitField):
	body = db.StringField(required=True)
	author = db.StringField(verbose_name="Author Name", required=True, max_length=255)


class Comment(db.EmbeddedDocument):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	body = db.StringField(verbose_name="Comment", required=True)
	author = db.StringField(verbose_name="Name", max_length=255, required=True)

#mocks
BB = BitBook()
BN1 = BitNote()
Q = Quote(title='A quote', body='long body', author='Adam Piotrowski')
BN1.bitfields.append(Q)
P = BlogPost(title='post', body='long post of a sexy blog post')
BN1.bitfields.append(P)


