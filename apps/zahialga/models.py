from django.db.models import Model, CharField, DateField, ForeignKey, CASCADE, IntegerField, TextField, BooleanField
import uuid
from apps.nom.models import Nom
from utils.model import JIL_CHOICES, HUIS_CHOICES, TOLBORIIN_TOLOV_CHOICES

class QpayToken(Model):
    token_type = CharField(max_length=20)
    refresh_expires_in = IntegerField()
    access_token = TextField()
    expires_in = IntegerField()
    refresh_token = TextField()
    
class Zahialga(Model):
    uuid4 = CharField(max_length=255, unique=True, editable=False)
    utas = CharField(max_length=8)
    ner = CharField(max_length=100)
    hend = CharField(max_length=100)
    jil = CharField(choices=JIL_CHOICES, max_length=100)
    huis = CharField(choices=HUIS_CHOICES, max_length=100)
    tolov = CharField(choices=TOLBORIIN_TOLOV_CHOICES, max_length=100, default='PENDING')
    torson_ognoo = DateField()
    uniin_dun = IntegerField()
    qpay_invoice_id = CharField(max_length=200, null=True)
    qpay_qr_text = TextField(null=True)
    qpay_qr_image = TextField(null=True)
    qpay_shortUrl = TextField(null=True)
    uussen_ognoo = DateField(auto_now_add=True)
    shinechlegdsen_ognoo = DateField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.uuid4:
            self.uuid4 = str(uuid.uuid4())
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.uuid4

class ZahialgaDeepLink(Model):
    zahialga = ForeignKey(Zahialga, on_delete=CASCADE)
    name = CharField(max_length=50, null=True)
    logo = CharField(max_length=200, null=True)
    link = TextField(null=True)
    
class ZahialgaNom(Model):
    zahialga = ForeignKey('zahialga', on_delete=CASCADE)    
    nom = ForeignKey(Nom, on_delete=CASCADE)
    une = IntegerField()
    
class ZahialgaHural(Model):
    zahialga = ForeignKey('zahialga', on_delete=CASCADE)
    mute_all = BooleanField(default=False)