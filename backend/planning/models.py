from django.db import models


class TypeTerrain(models.TextChoices):
    INTERIEUR = "INTERIEUR", "Intérieur"
    EXTERIEUR = "EXTERIEUR", "Extérieur"


class Terrain(models.Model):
    edition = models.ForeignKey("core.Edition", on_delete=models.PROTECT, related_name="terrains")
    nom = models.CharField(max_length=40)
    type_terrain = models.CharField(max_length=10, choices=TypeTerrain.choices)
    ordre = models.PositiveSmallIntegerField(default=0)
    est_actif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["edition", "nom"], name="unique_terrain_par_edition_nom")
        ]

    def __str__(self) -> str:
        return self.nom


class Creneau(models.Model):
    edition = models.ForeignKey("core.Edition", on_delete=models.PROTECT, related_name="creneaux")
    index = models.PositiveIntegerField()
    debut = models.DateTimeField()
    duree_minutes = models.PositiveSmallIntegerField(default=15)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["edition", "index"], name="unique_creneau_par_edition_index")
        ]

    def __str__(self) -> str:
        return f"Creneau {self.index}"
