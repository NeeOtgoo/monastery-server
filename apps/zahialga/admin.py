from django.contrib import admin
from .models import QpayToken, Zahialga, ZahialgaDeepLink, ZahialgaNom, ZahialgaHural

admin.site.register(QpayToken)
admin.site.register(Zahialga)
admin.site.register(ZahialgaDeepLink)
admin.site.register(ZahialgaNom)
admin.site.register(ZahialgaHural)