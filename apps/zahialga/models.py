from django.db.models import Model, CharField, DateField, ForeignKey, CASCADE, IntegerField
from apps.nom.models import Nom
from utils.model import JIL_CHOICES, HUIS_CHOICES, TOLBORIIN_TOLOV_CHOICES

class Zahialga(Model):
    ner = CharField(max_length=100)
    hend = CharField(max_length=100)
    torson_ognoo = DateField()
    jil = CharField(choices=JIL_CHOICES, max_length=100)
    huis = CharField(choices=HUIS_CHOICES, max_length=100)
    tolov = CharField(choices=TOLBORIIN_TOLOV_CHOICES, max_length=100, default='PENDING')
    uussen_ognoo = DateField(auto_now_add=True)
    shinechlegdsen_ognoo = DateField(auto_now=True)
    
class ZahialgaNom(Model):
    zahialga = ForeignKey('zahialga', on_delete=CASCADE)    
    nom = ForeignKey(Nom, on_delete=CASCADE)
    une = IntegerField()
    
