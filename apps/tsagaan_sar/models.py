from django.db.models import Model, CharField, DateField, ForeignKey, CASCADE
from apps.nom.models import Nom
from utils.model import SUUDAL_CHOICES, JIL_CHOICES, HUIS_CHOICES

class TsagaanSar(Model):
    ner = CharField(max_length=100)
    ognoo = DateField()

class TsagaanSarSuudal(Model):
    tsagaan_sar = ForeignKey(TsagaanSar, on_delete=CASCADE)
    suudal = CharField(choices=SUUDAL_CHOICES, max_length=100)
    jil = CharField(choices=JIL_CHOICES, max_length=100)
    huis = CharField(choices=HUIS_CHOICES, max_length=100)
    ognoo = DateField()

class TsagaaSarSuudalZasal(Model):
    tsagaan_sar_suudal = ForeignKey(TsagaanSarSuudal, on_delete=CASCADE)
    nom = ForeignKey(Nom, on_delete=CASCADE)
    
class BigiinToolol(Model):
    bilgiin_toolol = CharField(max_length=100)
    ognoo = DateField()