from django.db.models import Model, CharField, DateField, ForeignKey, CASCADE, IntegerField
import uuid
from apps.nom.models import Nom
from utils.model import JIL_CHOICES, HUIS_CHOICES, TOLBORIIN_TOLOV_CHOICES

class Zahialga(Model):
    uuid4 = CharField(max_length=255, unique=True, editable=False)
    utas = CharField(max_length=8)
    ner = CharField(max_length=100)
    hend = CharField(max_length=100)
    jil = CharField(choices=JIL_CHOICES, max_length=100)
    huis = CharField(choices=HUIS_CHOICES, max_length=100)
    tolov = CharField(choices=TOLBORIIN_TOLOV_CHOICES, max_length=100, default='PENDING')
    torson_ognoo = DateField()
    uussen_ognoo = DateField(auto_now_add=True)
    shinechlegdsen_ognoo = DateField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.uuid4:
            self.uuid4 = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
class ZahialgaNom(Model):
    zahialga = ForeignKey('zahialga', on_delete=CASCADE)    
    nom = ForeignKey(Nom, on_delete=CASCADE)
    une = IntegerField()