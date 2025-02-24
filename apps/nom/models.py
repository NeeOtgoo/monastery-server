from django.db.models import Model, CharField, IntegerField, ForeignKey, CASCADE, BooleanField

class Nomiin_torol(Model):
    ner = CharField(max_length=100)
    
class Nom(Model):
    ner = CharField(max_length=100)
    tailbar = CharField(max_length=400)
    une = IntegerField()
    online_zahialga_avah = BooleanField(default=True)
    
class NomBundle(Model):
    ner = CharField(max_length=100)
    tailbar = CharField(max_length=400)
    
class NomBundleNom(Model):
    nom_bundle = ForeignKey(NomBundle, on_delete=CASCADE)
    nom = ForeignKey(Nom, on_delete=CASCADE)