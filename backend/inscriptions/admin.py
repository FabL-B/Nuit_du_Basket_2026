from django.contrib import admin
from inscriptions.models import Equipe, Joueur


class EquipeAdmin(admin.ModelAdmin):
    pass


class JoueurAdmin(admin.ModelAdmin):
    pass


admin.site.register(Equipe, EquipeAdmin)
admin.site.register(Joueur, JoueurAdmin)
