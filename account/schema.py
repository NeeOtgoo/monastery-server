import graphene
from graphene_django.types import DjangoObjectType
from graphene.types.generic import GenericScalar
from django.contrib.auth import get_user_model
from graphql_jwt.shortcuts import get_token
from .models import CustomUser

class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name", "phone", "email"]

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    
    def resolve_me(self, info):
        try:
         return CustomUser.objects.get(pk=info.context.user.pk)
        except CustomUser.DoesNotExist:
            return None

class Login(graphene.Mutation):
    class Arguments:
        email = graphene.String()
        password = graphene.String()
        
    success = graphene.Boolean(default_value=False)
    errors = GenericScalar()
    token = graphene.String(default_value=None)
    
    @staticmethod
    def mutate(self, info, email, password):
        errors = {}
        success = False
        token = None

        try:
            user = get_user_model().objects.get(email=email)
            if user.check_password(password):
                success = True
                token = get_token(user)
            else:
                errors = {"password": "И-мэйл эсвэл нууц үг буруу байна"}
        except CustomUser.DoesNotExist as e:
            errors = {"password": "И-мэйл эсвэл нууц үг буруу байна"}
        
        return Login(success=success, errors=errors, token=token)

class Mutation(graphene.ObjectType):
    login = Login.Field()