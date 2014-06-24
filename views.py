from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView

from flask.ext.mongoengine.wtf import model_form
from bitnotes.models import Post, Comment, BitBook, BitNote, Quote, BlogPost, Code, Image, Rating

posts = Blueprint('posts', __name__, template_folder='templates')

class BitBookShelf(MethodView):

    form = model_form(BitBook, exclude=['created_at','cover_fields','bitnotes'])

    def get_context(self):
        context = {
            'form': self.form(request.form),
            'bitbooks': BitBook.objects.all(),
        }
        return context

    def get(self):
        context = self.get_context()
        return render_template('bookshelf.html', **context)

    def post(self):
        context = self.get_context()
        form = context.get('form')
        if form.validate():
            b = BitBook()
            form.populate_obj(b)
            b.save()
            return redirect(url_for('posts.bitbook', bitbook_id=b.id))
        return render_template('bookshelf.html', **context)


class BitBookView(MethodView):
    def get(self, bitbook_id):
        bitbook = BitBook.objects.get_or_404(id=bitbook_id)
        return render_template('bitbook.html', bitbook=bitbook)
    def post(self):
        pass


class BitNoteView(MethodView):

    
    def get(self, bitbook_id, bitnote_id):
        note = BitNote.objects.get_or_404(id=bitnote_id)
        bitbook = BitBook.objects.get_or_404(id=bitbook_id)
        unused_bitfields = bitbook.cover_fields
        for field in note.bitfields:
            if field.title in unused_bitfields:
                unused_bitfields.pop(field.title)
        unused_bitfields = unused_bitfields.values()
        return render_template('notes/note.html', note=note, bitbook=bitbook, unused_bitfields=unused_bitfields)

    def post(self, bitbook_id, bitnote_id):
        note = BitNote.objects.get_or_404(id=bitnote_id)
        field_type = request.form['field_type']
        field_title = request.form['field_title']
        field = [x for x in note.bitfields if x.title == field_title][0]
        if field:
            constructor = globals()[field_type]
            mform = model_form(constructor, exclude=['created_at','title'])
            form = mform(request.form)
            form.populate_obj(field)
            note.save()

        return render_template('notes/note.html', note=note)       

class BitNoteManager(MethodView):
    def post(self, bitbook_id):
        bitbook = BitBook.objects.get_or_404(id=bitbook_id)
        action = request.form['action']
        if action == 'create':
            note = BitNote()
            #note.bitfields.append(bitbook.cover_fields.values())
            note.save()
            bitbook.bitnotes.append(note)
            bitbook.save()
            return redirect(url_for('posts.bitnote', bitbook_id=bitbook.id, bitnote_id=note.id))


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

        if task == 'update':
            if (not[ x for x in note.bitfields if x.title == field_title]) and (field_title in bitbook.cover_fields):
                note.bitfields.append(bitbook.cover_fields[field_title])
                note.save()

        return redirect(url_for('posts.bitnote', bitbook_id=bitbook_id, bitnote_id = note.id))



class ListView(MethodView):
    def get(self):
        posts = Post.objects.all()
        return render_template('posts/list.html', posts=posts)


class DetailView(MethodView):

    form = model_form(Comment, exclude=['created_at'])

    def get_context(self, slug):
        post = Post.objects.get_or_404(slug=slug)
        form = self.form(request.form)

        context = {
            "post": post,
            "form": form
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('posts/detail.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            comment = Comment()
            form.populate_obj(comment)

            post = context.get('post')
            post.comments.append(comment)
            post.save()

            return redirect(url_for('posts.detail', slug=slug))
        return render_template('posts/detail.html', **context)


# Register the urls
#posts.add_url_rule('/', view_func=ListView.as_view('list'))
#posts.add_url_rule('/<slug>/', view_func=DetailView.as_view('detail'))
posts.add_url_rule('/<bitbook_id>/', view_func=BitBookView.as_view('bitbook'))
#posts.add_url_rule('/bn/<bitnote_id>/',view_func=BitNoteView.as_view('bitnote'))
posts.add_url_rule('/<bitbook_id>/<bitnote_id>/field_manager',view_func=FieldManager.as_view('field_manager'))
posts.add_url_rule('/', view_func=BitBookShelf.as_view('bitbooks'))
posts.add_url_rule('/<bitbook_id>/<bitnote_id>/', view_func=BitNoteView.as_view('bitnote'))
posts.add_url_rule('/<bitbook_id>/note_manager', view_func=BitNoteManager.as_view('bitnote_manager'))


