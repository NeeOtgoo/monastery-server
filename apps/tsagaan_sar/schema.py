import graphene
from graphene_django.types import DjangoObjectType
from .models import TsagaanSar, TsagaanSarSuudal, TsagaaSarSuudalZasal, BigiinToolol
from utils.utils import calculate_mongolian_zodiac
from apps.nom.models import Nom
from apps.nom.schema import NomType
from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from datetime import date

class TsagaanSarType(DjangoObjectType):
    class Meta:
        model = TsagaanSar

class JilType(graphene.ObjectType):
    year = graphene.Int()
    animal = graphene.String()
    element = graphene.String()
    
class TsagaanSarSuudalType(DjangoObjectType):
    class Meta:
        model = TsagaanSarSuudal
        # fields = ["id", "tsagaan_sar", "suudal", "jil", "huis", "ognoo"]

class TsagaaSarSuudalZasalType(DjangoObjectType):
    class Meta:
        model = TsagaaSarSuudalZasal
        # fields = ["id", "tsagaan_sar_suudal", "nom"]

class BilgiinToololType(DjangoObjectType):
    class Meta:
        model = BigiinToolol
        fields = ["id", "bilgiin_toolol", "ognoo"]

class TsagaanSarSuudalInputType(graphene.InputObjectType):
    id = graphene.String(required=True)
    suudal = graphene.String(required=True)
    jil = graphene.String(required=True)
    huis = graphene.String(required=True)
    ognoo = graphene.Date()
    nom = graphene.List(graphene.String)
 
class Query(graphene.ObjectType):
    tsagaan_sar = graphene.List(TsagaanSarType)
    tsagaan_sar_by_id = graphene.Field(TsagaanSarType, id=graphene.Int(required=True))
    jil_ognoogoor = graphene.Field(JilType, ognoo=graphene.Int(required=True))
    all_tsagaan_sar_suudal = graphene.List(TsagaanSarSuudalType, tsagaan_sar_id=graphene.ID(required=True))
    all_tsagaan_sariin_suudal_zasal = graphene.List(TsagaaSarSuudalZasalType, tsagaan_sar_suudal_id=graphene.Int(required=True))
    tsagaan_sar_suudal_zasal_nom = graphene.List(NomType, jil=graphene.String(required=True), huis=graphene.String(required=True), ognoo=graphene.Int(required=True))
    all_bilgiin_toolol = graphene.List(BilgiinToololType)
    todays_bilgiin_toolol = graphene.Field(BilgiinToololType)
    
    @login_required
    def resolve_tsagaan_sar(self, info):
        return TsagaanSar.objects.all()
    
    @login_required
    def resolve_tsagaan_sar_by_id(self, info, id):
        return TsagaanSar.objects.get(pk=id)
    
    @login_required
    def resolve_all_tsagaan_sar_suudal(self, info, tsagaan_sar_id):

        tsagaan_sar = TsagaanSar.objects.get(pk=tsagaan_sar_id)

        return TsagaanSarSuudal.objects.filter(tsagaan_sar=tsagaan_sar).order_by('-ognoo')
    
    @login_required
    def resolve_all_tsagaan_sariin_suudal_zasal(self, info, tsagaan_sar_suudal_id):
        
        tsagaan_sar_suudal = TsagaanSarSuudal.objects.get(pk=tsagaan_sar_suudal_id)
        
        return TsagaaSarSuudalZasal.objects.filter(tsagaan_sar_suudal=tsagaan_sar_suudal)
    
    def resolve_jil_ognoogoor(self, info, ognoo):

        jil = calculate_mongolian_zodiac(ognoo)
        
        return JilType(
            year=jil['year'],
            animal=jil['animal'],
            element=jil['element']
        )

    def resolve_tsagaan_sar_suudal_zasal_nom(self, info, jil, huis, ognoo):
        
        try:
            suudal_o = TsagaanSarSuudal.objects.get(jil=jil, huis=huis, ognoo__year=ognoo)
        except TsagaanSarSuudal.DoesNotExist:
            raise GraphQLError("Таны оруулсан мэдээлэл буруу байна")
        return Nom.objects.filter(tsagaasarsuudalzasal__tsagaan_sar_suudal=suudal_o) 
    
    @login_required
    def resolve_all_bilgiin_toolol(self, info):
        return BigiinToolol.objects.filter(ognoo__gte=date.today()).order_by('-ognoo')
    
    def resolve_todays_bilgiin_toolol(self, info):
        
        try:
            return BigiinToolol.objects.get(ognoo=date.today())
        except BigiinToolol.DoesNotExist:
            dummy_object = BigiinToolol(ognoo=date.today(), bilgiin_toolol="Мэдээлэл байхгүй", id=1)
            return dummy_object
    
class CreateOrUpdateTsagaanSar(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        ner = graphene.String(required=True)
        ognoo = graphene.Date(required=True)

    tsagaan_sar = graphene.Field(TsagaanSarType)

    @login_required
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

    @login_required
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

    @login_required
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

    @login_required
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

    @login_required
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

    @login_required
    def mutate(self, info, id):
        try:
            tsagaa_sar_suudal_zasal = TsagaaSarSuudalZasal.objects.get(pk=id)
            tsagaa_sar_suudal_zasal.delete()
            return DeleteTsagaaSarSuudalZasal(success=True)
        except TsagaaSarSuudalZasal.DoesNotExist:
            return DeleteTsagaaSarSuudalZasal(success=False)

class MassStoreTsagaanSarSuudal(graphene.Mutation):
    
    class Arguments:
        tsagaan_sar = graphene.ID()
        suudal = graphene.List(TsagaanSarSuudalInputType)
    
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, tsagaan_sar, suudal):
        
        tsagaan_sar_o = TsagaanSar.objects.get(pk=tsagaan_sar)
        
        for s in suudal:
            suudal_o = TsagaanSarSuudal.objects.create(
                tsagaan_sar=tsagaan_sar_o,
                suudal=s.suudal,
                jil=s.jil,
                huis=s.huis,
                ognoo=s.ognoo
            )
            
            for n in s.nom:
                nom_o = Nom.objects.get(pk=n)
                TsagaaSarSuudalZasal.objects.create(
                    tsagaan_sar_suudal=suudal_o,
                    nom=nom_o
                )
        return MassStoreTsagaanSarSuudal(success=True)
 
class CreateOrUpdateBigiinToolol(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        bilgiin_toolol = graphene.String(required=True)
        ognoo = graphene.Date(required=True)

    bigiin_toolol = graphene.Field(BilgiinToololType)

    @login_required
    def mutate(self, info, id=None, bilgiin_toolol=None, ognoo=None):
        if id:
            bigiin_toolol = BigiinToolol.objects.get(pk=id)
            bigiin_toolol.bilgiin_toolol = bilgiin_toolol
            bigiin_toolol.ognoo = ognoo
            bigiin_toolol.save()
        else:
            bigiin_toolol = BigiinToolol.objects.create(bilgiin_toolol=bilgiin_toolol, ognoo=ognoo)
        return CreateOrUpdateBigiinToolol(bigiin_toolol=bigiin_toolol)
    
class DeleteBigiinToolol(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        try:
            bigiin_toolol = BigiinToolol.objects.get(pk=id)
            bigiin_toolol.delete()
            return DeleteBigiinToolol(success=True)
        except BigiinToolol.DoesNotExist:
            return DeleteBigiinToolol(success=False)
        
class Mutation(graphene.ObjectType):
    create_or_update_tsagaan_sar = CreateOrUpdateTsagaanSar.Field()
    delete_tsagaan_sar = DeleteTsagaanSar.Field()
    create_or_update_tsagaan_sar_suudal = CreateOrUpdateTsagaanSarSuudal.Field()
    delete_tsagaan_sar_suudal = DeleteTsagaanSarSuudal.Field()
    create_or_update_tsagaa_sar_suudal_zasal = CreateOrUpdateTsagaaSarSuudalZasal.Field()
    delete_tsagaa_sar_suudal_zasal = DeleteTsagaaSarSuudalZasal.Field()
    mass_store_tsagaan_sar_suudal = MassStoreTsagaanSarSuudal.Field()
    create_or_update_bigiin_toolol = CreateOrUpdateBigiinToolol.Field()
    delete_bigiin_toolol = DeleteBigiinToolol.Field()