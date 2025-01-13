from django.db.models import Model, CharField, IntegerField, ForeignKey, CASCADE
from apps.tsagaan_sar.models import TsagaanSar

# Create your models here.
class Nomiin_torol(Model):
    ner = CharField(max_length=100)
    
class Nom(Model):
    ner = CharField(max_length=100)
    tailbar = CharField(max_length=400)
    une = IntegerField()
    
class TsagaanSariinNom(Model):
    tsagaan_sar = ForeignKey(TsagaanSar, on_delete=CASCADE, related_name="tsagaan_sar")
    nom = ForeignKey(Nom, on_delete=CASCADE, related_name="nom")