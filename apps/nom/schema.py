import graphene
from graphene_django.types import DjangoObjectType
from .models import Nomiin_torol, Nom, TsagaanSariinNom
from utils.utils import custom_paginate

class Nomiin_torolType(DjangoObjectType):
    class Meta:
        model = Nomiin_torol
        fields = ["id", "ner"]
        
class NomType(DjangoObjectType):
    class Meta:
        model = Nom
        fields = ["id", "ner", "tailbar", "une"]
        
class TsagaanSariinNomType(DjangoObjectType):
    class Meta:
        model = TsagaanSariinNom
        fields = ["id", "tsagaan_sar", "nom"]

class NomFilterInputType(graphene.InputObjectType):
    ner = graphene.String()
    tailbar = graphene.String()

class NomPaginationType(graphene.ObjectType):
    page = graphene.Int()
    per_page = graphene.Int()
    page_count = graphene.Int()
    total_count = graphene.Int()
    records = graphene.List(NomType)
  
class Query(graphene.ObjectType):
    nomiin_torol = graphene.List(Nomiin_torolType)
    nom = graphene.Field(
        NomPaginationType,
        page=graphene.Int(), 
        per_page=graphene.Int(), 
        filter=NomFilterInputType()
    )
    tsagaan_sariin_nom = graphene.List(TsagaanSariinNomType)
    nomiin_torol_by_id = graphene.Field(Nomiin_torolType, id=graphene.Int(required=True))
    nom_by_id = graphene.Field(NomType, id=graphene.Int(required=True))
    tsagaan_sariin_nom_by_id = graphene.Field(TsagaanSariinNomType, id=graphene.Int(required=True))

    def resolve_nomiin_torol(self, info):
        return Nomiin_torol.objects.all()

    def resolve_nom(self, info, page, per_page, filter):
        
        query_set = Nom.objects.filter(
            **({
                "ner__icontains": filter.get("ner")
            } if filter.get("ner") else {}),
            **({
                "tailbar__icontains": filter.get("tailbar")
            } if filter.get("tailbar") else {})
        )
        
        jobs = custom_paginate(
            query_set.order_by('-pk'), 
            int(page), 
            int(per_page)
        )
        
        return {
            **jobs,
            'page': page,
            'per_page': per_page
        }

    def resolve_tsagaan_sariin_nom(self, info):
        return TsagaanSariinNom.objects.all()
    
    def resolve_nomiin_torol_by_id(self, info, id):
        return Nomiin_torol.objects.get(pk=id)
    
    def resolve_nom_by_id(self, info, id):
        return Nom.objects.get(pk=id)