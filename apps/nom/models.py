from django.db.models import Model, CharField, IntegerField

# Create your models here.
class Nomiin_torol(Model):
    ner = CharField(max_length=100)
    
class Nom(Model):
    ner = CharField(max_length=100)
    tailbar = CharField(max_length=400)
    une = IntegerField()