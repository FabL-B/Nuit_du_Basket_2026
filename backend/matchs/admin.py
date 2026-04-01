from django.contrib import admin
from matchs.models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "edition",
        "phase_globale",
        "sous_phase",
        "groupe",
        "display_equipe_a",
        "display_equipe_b",
        "statut",
        "creneau",
        "terrain",
        "tour_finale",
        "numero_tour",
    )
    list_filter = (
        "edition",
        "phase_globale",
        "sous_phase",
        "statut",
        "tour_finale",
    )
    search_fields = (
        "libelle_equipe_a",
        "libelle_equipe_b",
        "equipe_a__nom",
        "equipe_b__nom",
        "groupe__code",
    )
    readonly_fields = ("cree_le", "modifie_le")

    fieldsets = (
        (
            "Contexte",
            {
                "fields": (
                    "edition",
                    "phase_globale",
                    "sous_phase",
                    "groupe",
                )
            },
        ),
        (
            "Participants",
            {
                "fields": (
                    "equipe_a",
                    "libelle_equipe_a",
                    "equipe_b",
                    "libelle_equipe_b",
                    "vainqueur",
                )
            },
        ),
        (
            "Planification",
            {
                "fields": (
                    "creneau",
                    "terrain",
                    "statut",
                    "tour_finale",
                    "numero_tour",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": ("cree_le", "modifie_le"),
            },
        ),
    )

    @admin.display(description="Équipe A")
    def display_equipe_a(self, obj):
        return obj.equipe_a.nom if obj.equipe_a else obj.libelle_equipe_a

    @admin.display(description="Équipe B")
    def display_equipe_b(self, obj):
        return obj.equipe_b.nom if obj.equipe_b else obj.libelle_equipe_b
