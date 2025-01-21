import graphene
from graphene_django.types import DjangoObjectType
from .models import TsagaanSar, TsagaanSarSuudal, TsagaaSarSuudalZasal
from utils.utils import calculate_mongolian_zodiac
from apps.nom.models import Nom

class TsagaanSarType(DjangoObjectType):
    class Meta:
        model = TsagaanSar
        fields = ["id", "ner", "ognoo"]

class JilType(graphene.ObjectType):
    year = graphene.Int()
    animal = graphene.String()
    element = graphene.String()
    
class TsagaanSarSuudalType(DjangoObjectType):
    class Meta:
        model = TsagaanSarSuudal
        fields = ["id", "tsagaan_sar", "suudal", "jil", "huis", "ognoo"]

class TsagaaSarSuudalZasalType(DjangoObjectType):
    class Meta:
        model = TsagaaSarSuudalZasal
        fields = ["id", "tsagaan_sar_suudal", "nom"]
    
class Query(graphene.ObjectType):
    tsagaan_sar = graphene.List(TsagaanSarType)
    tsagaan_sar_by_id = graphene.Field(TsagaanSarType, id=graphene.Int(required=True))
    jil_ognoogoor = graphene.Field(JilType, ognoo=graphene.Int(required=True))

    def resolve_tsagaan_sar(self, info):
        return TsagaanSar.objects.all()
    
    def resolve_tsagaan_sar_by_id(self, info, id):
        return TsagaanSar.objects.get(pk=id)
    
    def resolve_jil_ognoogoor(self, info, ognoo):

        jil = calculate_mongolian_zodiac(ognoo)
        
        return JilType(
            year=jil['year'],
            animal=jil['animal'],
            element=jil['element']
        )

class CreateOrUpdateTsagaanSar(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        ner = graphene.String(required=True)
        ognoo = graphene.Date(required=True)

    tsagaan_sar = graphene.Field(TsagaanSarType)

    def mutate(self, info, id=None, ner=None, ognoo=None):
        if id:
            tsagaan_sar = TsagaanSar.objects.get(pk=id)
            tsagaan_sar.ner = ner
            tsagaan_sar.ognoo = ognoo
            tsagaan_sar.save()
        else:
            tsagaan_sar = TsagaanSar.objects.create(ner=ner, ognoo=ognoo)
        return CreateOrUpdateTsagaanSar(tsagaan_sar=tsagaan_sar)
    
class DeleteTsagaanSar(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            tsagaan_sar = TsagaanSar.objects.get(pk=id)
            tsagaan_sar.delete()
            return DeleteTsagaanSar(success=True)
        except TsagaanSar.DoesNotExist:
            return DeleteTsagaanSar(success=False)

class CreateOrUpdateTsagaanSarSuudal(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        tsagaan_sar_id = graphene.Int(required=True)
        suudal = graphene.String(required=True)
        jil = graphene.String(required=True)
        huis = graphene.String(required=True)
        ognoo = graphene.Date(required=True)

    tsagaan_sar_suudal = graphene.Field(TsagaanSarSuudalType)

    def mutate(self, info, tsagaan_sar_id, suudal, jil, huis, ognoo, id=None):
        if id:
            tsagaan_sar_suudal = TsagaanSarSuudal.objects.get(pk=id)
            tsagaan_sar_suudal.tsagaan_sar_id = tsagaan_sar_id
            tsagaan_sar_suudal.suudal = suudal
            tsagaan_sar_suudal.jil = jil
            tsagaan_sar_suudal.huis = huis
            tsagaan_sar_suudal.ognoo = ognoo
            tsagaan_sar_suudal.save()
        else:
            tsagaan_sar_suudal = TsagaanSarSuudal.objects.create(
                tsagaan_sar_id=tsagaan_sar_id,
                suudal=suudal,
                jil=jil,
                huis=huis,
                ognoo=ognoo
            )
        return CreateOrUpdateTsagaanSarSuudal(tsagaan_sar_suudal=tsagaan_sar_suudal)
    
class DeleteTsagaanSarSuudal(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            tsagaan_sar_suudal = TsagaanSarSuudal.objects.get(pk=id)
            tsagaan_sar_suudal.delete()
            return DeleteTsagaanSarSuudal(success=True)
        except TsagaanSarSuudal.DoesNotExist:
            return DeleteTsagaanSarSuudal(success=False)

class CreateOrUpdateTsagaaSarSuudalZasal(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        tsagaan_sar_suudal_id = graphene.Int(required=True)
        nom_id = graphene.Int(required=True)

    tsagaa_sar_suudal_zasal = graphene.Field(TsagaaSarSuudalZasalType)

    def mutate(self, info, tsagaan_sar_suudal_id, nom_id, id=None):
        
        nom_o = Nom.objects.get(pk=nom_id)
        
        if id:
            tsagaa_sar_suudal_zasal = TsagaaSarSuudalZasal.objects.get(pk=id)
            tsagaa_sar_suudal_zasal.tsagaan_sar_suudal_id = tsagaan_sar_suudal_id
            tsagaa_sar_suudal_zasal.nom = nom_o
            tsagaa_sar_suudal_zasal.save()
        else:
            tsagaa_sar_suudal_zasal = TsagaaSarSuudalZasal.objects.create(
                tsagaan_sar_suudal_id=tsagaan_sar_suudal_id,
                nom=nom_o
            )
        return CreateOrUpdateTsagaaSarSuudalZasal(tsagaa_sar_suudal_zasal=tsagaa_sar_suudal_zasal)
    
class DeleteTsagaaSarSuudalZasal(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            tsagaa_sar_suudal_zasal = TsagaaSarSuudalZasal.objects.get(pk=id)
            tsagaa_sar_suudal_zasal.delete()
            return DeleteTsagaaSarSuudalZasal(success=True)
        except TsagaaSarSuudalZasal.DoesNotExist:
            return DeleteTsagaaSarSuudalZasal(success=False)
        
class Mutation(graphene.ObjectType):
    create_or_update_tsagaan_sar = CreateOrUpdateTsagaanSar.Field()
    delete_tsagaan_sar = DeleteTsagaanSar.Field()
    create_or_update_tsagaan_sar_suudal = CreateOrUpdateTsagaanSarSuudal.Field()
    delete_tsagaan_sar_suudal = DeleteTsagaanSarSuudal.Field()
    create_or_update_tsagaa_sar_suudal_zasal = CreateOrUpdateTsagaaSarSuudalZasal.Field()
    delete_tsagaa_sar_suudal_zasal = DeleteTsagaaSarSuudalZasal.Field()