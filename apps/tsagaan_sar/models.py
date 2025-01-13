from django.db.models import Model, CharField, DateField

class TsagaanSar(Model):
    ner = CharField(max_length=100)
    ognoo = DateField()