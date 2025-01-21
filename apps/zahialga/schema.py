import graphene
from graphene_django.types import DjangoObjectType
from .models import Zahialga, ZahialgaNom

class ZahialgaType(DjangoObjectType):
    class Meta:
        model = Zahialga
        fields = ["id", "utas", "ner", "hend", "jil", "huis", "tolov", "torson_ognoo", "uussen_ognoo", "shinechlegdsen_ognoo"]
        
class ZahialgaNomType(DjangoObjectType):
    class Meta:
        model = ZahialgaNom
        fields = ["id", "zahialga", "nom", "une"]

class ZahialgaNomInputType(graphene.ObjectType):
    nom = graphene.ID(required=True)
    une = graphene.Int()
    

class Query(graphene.ObjectType):
    check_invoice = graphene.Field(ZahialgaType, utas=graphene.Int(required=True))
    
class CreateZahialga(graphene.Mutation):
    utas = graphene.Int(required=True)
    ner = graphene.String(required=True)
    hend = graphene.String(required=True)
    jil = graphene.String(required=True)