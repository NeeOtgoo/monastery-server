import graphene
from graphene_django.types import DjangoObjectType
from graphene.types.generic import GenericScalar
from .models import Contact

class ContactType(DjangoObjectType):
    class Meta:
        model = Contact
        fields = ["id", "ner", "utas", "huselt"]

class CreateContact(graphene.Mutation):
    class Arguments:
        ner = graphene.String()
        utas = graphene.String()
        huselt = graphene.String()
    
    success = graphene.Boolean(default_value=False)
    errors = GenericScalar()
    
    @staticmethod
    def mutate(self, info, ner, utas, huselt):
        errors = {}
        success = False
        
        if not ner or len(ner.strip()) > 50:
            errors["ner"] = "Нэр заавал оруулах бөгөөд 50-с бага үсэгтэй байх ёстой."

        if not utas or not utas.isdigit() or len(utas) != 8:
            errors["utas"] = "Утасны дугаар заавал 8 оронтой тоо байх ёстой."

        if not huselt or len(huselt.strip()) > 500:
            errors["huselt"] = "Хүсэлт хамгийн багадаа 500-с бага үсэгтэй байх шаардлагатай."

        if not errors:
            
            Contact.objects.create(
                ner = ner,
                utas = utas,
                huselt = huselt
            )
            
            success = True
        
        return CreateContact(success=success, errors=errors, )

class Mutation(graphene.ObjectType):
    create_contact = CreateContact.Field()