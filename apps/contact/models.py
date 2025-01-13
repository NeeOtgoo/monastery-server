from django.db.models import Model, CharField

class Contact(Model):
    ner = CharField(max_length=100)
    utas = CharField(max_length=100)
    huselt = CharField(max_length=500)