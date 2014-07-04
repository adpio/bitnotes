from models import *
from loremipsum import get_paragraphs, get_sentences

def performance_test_1():
	u = User.objects.get(email='a.piotrowski@g.pl')
	for x in range(50):
		bb = BitBook(title='A new bitbook number %s'%x, description=get_sentences(1)[0])
		bb.save()
		for y in range(100):
			bn = BitNote()
			bn.save()
			bf1 = BlogPost(title='blog post 1', body=''.join(get_paragraphs(10)))
			bf2 = Quote(title='a fancy qoute', body=get_sentences(1)[0], author='Author Aouthorski')
			bf3 = Rating(title='rating')
			bn.bitfields.append(bf1)
			bn.bitfields.append(bf2)
			bn.bitfields.append(bf3)
			bn.save()
			bn.save_to_bitbook(bitbook=bb)
		u.bitbooks.append(bb)
		u.save()
		print 'bb no %s'%x
