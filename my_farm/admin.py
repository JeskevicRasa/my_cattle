from django.contrib import admin
from .models import Cattle


class CattleAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'breed', 'birth_date', 'entry_date', 'end_date']
    ordering = ['name']


admin.site.register(Cattle)

