from django.contrib import admin
from groupes.models import Groupe, GroupeEquipe


class GroupeAdmin(admin.ModelAdmin):
    pass


class GroupeEquipeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Groupe, GroupeAdmin)
admin.site.register(GroupeEquipe, GroupeEquipeAdmin)
