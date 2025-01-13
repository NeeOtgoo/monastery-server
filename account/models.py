from django.db.models import CharField
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = CharField(max_length=20, unique=True)
    
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["username"]