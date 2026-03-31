from django.contrib import admin
from tournois.models import Tournoi


class TournoiAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tournoi, TournoiAdmin)
