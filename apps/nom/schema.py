import graphene
from graphene_django.types import DjangoObjectType
from .models import Nomiin_torol, Nom
from utils.utils import custom_paginate

class Nomiin_torolType(DjangoObjectType):
    class Meta:
        model = Nomiin_torol
        fields = ["id", "ner"]
        
class NomType(DjangoObjectType):
    class Meta:
        model = Nom
        fields = ["id", "ner", "tailbar", "une"]

class NomInputType(graphene.InputObjectType):
    ner = graphene.String()
    tailbar = graphene.String()
    une = graphene.Int()

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
    nomiin_torol_by_id = graphene.Field(Nomiin_torolType, id=graphene.Int(required=True))
    nom_by_id = graphene.Field(NomType, id=graphene.Int(required=True))
    all_noms = graphene.List(NomType)

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
    
    def resolve_nomiin_torol_by_id(self, info, id):
        return Nomiin_torol.objects.get(pk=id)
    
    def resolve_nom_by_id(self, info, id):
        return Nom.objects.get(pk=id)
    
class CreateOrUpdateNom(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=False)
        ner = graphene.String(required=True)
        tailbar = graphene.String(required=True)
        une = graphene.Int(required=True)

    nom = graphene.Field(NomType)

    def mutate(self, info, ner, tailbar, une, id=None):
        if id:
            nom = Nom.objects.get(pk=id)
            nom.ner = ner
            nom.tailbar = tailbar
            nom.une = une
            nom.save()
        else:
            nom = Nom.objects.create(ner=ner, tailbar=tailbar, une=une)
        return CreateOrUpdateNom(nom=nom)

class DeleteNom(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            nom = Nom.objects.get(pk=id)
            nom.delete()
            return DeleteNom(success=True)
        except Nom.DoesNotExist:
            return DeleteNom(success=False)

class MassStoreNom(graphene.Mutation):
    class Arguments:
        nom = graphene.List(NomInputType)
        
    success = graphene.Boolean()
    
    def mutate(self, info, nom):
        for n in nom:
            Nom.objects.create(ner=n.ner, tailbar=n.tailbar, une=n.une)
        return MassStoreNom(success=True)

class Mutation(graphene.ObjectType):
    create_or_update_nom = CreateOrUpdateNom.Field()
    delete_nom = DeleteNom.Field()
    mass_store_nom = MassStoreNom.Field()