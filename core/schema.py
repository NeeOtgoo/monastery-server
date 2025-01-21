import graphene
import account.schema
import apps.tsagaan_sar.schema
import apps.nom.schema
import apps.contact.schema

class Query(
    account.schema.Query,
    apps.tsagaan_sar.schema.Query,
    apps.nom.schema.Query,
    graphene.ObjectType
):
    pass

class Mutation(
    account.schema.Mutation,
    apps.contact.schema.Mutation,
    apps.tsagaan_sar.schema.Mutation,
    apps.nom.schema.Mutation,
    graphene.ObjectType
):
    pass
    

schema = graphene.Schema(query=Query, mutation=Mutation)