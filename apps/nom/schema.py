import graphene
from graphene_django.types import DjangoObjectType
from .models import Nomiin_torol, Nom, NomBundle, NomBundleNom
from utils.utils import custom_paginate

class Nomiin_torolType(DjangoObjectType):
    class Meta:
        model = Nomiin_torol
        fields = ["id", "ner"]
        
class NomType(DjangoObjectType):
    class Meta:
        model = Nom
        fields = ["id", "ner", "tailbar", "une", "online_zahialga_avah"]

class NomBundleType(DjangoObjectType):
    class Meta:
        model = NomBundle
        fields = ["id", "ner", "tailbar"]
        
class NomBundleNomType(DjangoObjectType):
    class Meta:
        model = NomBundleNom
        fields = ["id", "nom_bundle", "nom"]

class NomInputType(graphene.InputObjectType):
    id = graphene.String()
    ner = graphene.String()
    tailbar = graphene.String()
    une = graphene.Int()
    online_zahialga_avah = graphene.Boolean()
    
class NomFilterInputType(graphene.InputObjectType):
    ner = graphene.String()
    tailbar = graphene.String()
    online_zahialga_avah = graphene.Boolean()

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
    all_nom_bundles = graphene.List(NomBundleType)
    nom_bundle_by_id = graphene.Field(NomBundleType, id=graphene.Int(required=True))
    all_nom_bundle_noms = graphene.List(NomBundleNomType, nom_bundle=graphene.ID())

    def resolve_nomiin_torol(self, info):
        return Nomiin_torol.objects.all()

    def resolve_nom(self, info, page, per_page, filter):
            
        query_params = {}

        # True үед зөвхөн True утгатай өгөгдлийг шүүх
        if filter.get("online_zahialga_avah") is True:
            query_params["online_zahialga_avah"] = True

        # Бусад хайлтын нөхцлүүд
        if filter.get("ner"):
            query_params["ner__icontains"] = filter["ner"]

        if filter.get("tailbar"):
            query_params["tailbar__icontains"] = filter["tailbar"]

        # Query-г үүсгэж, эрэмбэлэх
        query_set = Nom.objects.filter(**query_params).order_by("ner")

        
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
    
    def resolve_all_nom_bundles(self, info):
        return NomBundle.objects.all()
    
    def resolve_all_nom_bundle_noms(self, info, nom_bundle):
        
        nom_bundle_o = NomBundle.objects.get(pk=nom_bundle)
        
        return NomBundleNom.objects.filter(nom_bundle=nom_bundle_o)
    
    def resolve_all_noms(self, info):
        return Nom.objects.all()
    
    def resolve_nom_bundle_by_id(self, info, id):
        return NomBundle.objects.get(pk=id)
    
class CreateOrUpdateNom(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=False)
        ner = graphene.String(required=True)
        tailbar = graphene.String(required=True)
        une = graphene.Int(required=True)
        online_zahialga_avah = graphene.Boolean(required=True)

    nom = graphene.Field(NomType)

    def mutate(self, info, ner, tailbar, une, online_zahialga_avah, id=None):
        if id:
            nom = Nom.objects.get(pk=id)
            nom.ner = ner
            nom.tailbar = tailbar
            nom.une = une
            nom.online_zahialga_avah = online_zahialga_avah
            nom.save()
        else:
            nom = Nom.objects.create(ner=ner, tailbar=tailbar, une=une, online_zahialga_avah=online_zahialga_avah)
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
            Nom.objects.create(ner=n.ner, tailbar=n.tailbar, une=n.une, id=n.id, online_zahialga_avah=n.online_zahialga_avah)
        return MassStoreNom(success=True)

class CreateOrUpdateNomBundle(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=False)
        ner = graphene.String(required=True)
        tailbar = graphene.String(required=True)

    nom_bundle = graphene.Field(NomBundleType)

    def mutate(self, info, ner, tailbar, id=None):
        if id:
            nom_bundle = NomBundle.objects.get(pk=id)
            nom_bundle.ner = ner
            nom_bundle.tailbar = tailbar
            nom_bundle.save()
        else:
            nom_bundle = NomBundle.objects.create(ner=ner, tailbar=tailbar)
        return CreateOrUpdateNomBundle(nom_bundle=nom_bundle)

class DeleteNomBundle(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            nom_bundle = NomBundle.objects.get(pk=id)
            nom_bundle.delete()
            return DeleteNomBundle(success=True)
        except NomBundle.DoesNotExist:
            return DeleteNomBundle(success=False)
        
class CreateOrUpdateNomBundleNom(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=False)
        nom_bundle_id = graphene.Int(required=True)
        nom_id = graphene.Int(required=True)

    nom_bundle_nom = graphene.Field(NomBundleNomType)

    def mutate(self, info, nom_bundle_id, nom_id, id=None):
            
        nom_o = Nom.objects.get(pk=nom_id)
        nom_bundle_o = NomBundle.objects.get(pk=nom_bundle_id)
        
        if id:
            nom_bundle_nom = NomBundleNom.objects.get(pk=id)
            nom_bundle_nom.nom_bundle = nom_bundle_o
            nom_bundle_nom.nom = nom_o
            nom_bundle_nom.save()
        else:
            nom_bundle_nom = NomBundleNom.objects.create(nom_bundle=nom_bundle_o, nom=nom_o)
        return CreateOrUpdateNomBundleNom(nom_bundle_nom=nom_bundle_nom)
    
class DeleteNomBundleNom(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            nom_bundle_nom = NomBundleNom.objects.get(pk=id)
            nom_bundle_nom.delete()
            return DeleteNomBundleNom(success=True)
        except NomBundleNom.DoesNotExist:
            return DeleteNomBundleNom(success=False)

class Mutation(graphene.ObjectType):
    create_or_update_nom = CreateOrUpdateNom.Field()
    delete_nom = DeleteNom.Field()
    mass_store_nom = MassStoreNom.Field()
    create_or_update_nom_bundle = CreateOrUpdateNomBundle.Field()
    delete_nom_bundle = DeleteNomBundle.Field()
    create_or_update_nom_bundle_nom = CreateOrUpdateNomBundleNom.Field()
    delete_nom_bundle_nom = DeleteNomBundleNom.Field()