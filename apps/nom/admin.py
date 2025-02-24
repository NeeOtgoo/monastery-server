from django.contrib import admin
from .models import Nom, NomBundle, NomBundleNom
# Register your models here.

admin.site.register(Nom)
admin.site.register(NomBundle)
admin.site.register(NomBundleNom)