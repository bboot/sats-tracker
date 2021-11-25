from django.contrib import admin

from .models import TxOut, Actor

# Register your models here.
admin.site.register(TxOut)
admin.site.register(Actor)
