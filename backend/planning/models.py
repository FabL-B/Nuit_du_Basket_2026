from django.core.exceptions import ValidationError
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
            models.UniqueConstraint(
                fields=["edition", "nom"], name="unique_terrain_par_edition_nom"
            )
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
            models.UniqueConstraint(
                fields=["edition", "index"], name="unique_creneau_par_edition_index"
            )
        ]

    def __str__(self) -> str:
        return f"Creneau {self.index}"


class PausePlanning(models.Model):
    edition = models.ForeignKey(
        "core.Edition", on_delete=models.PROTECT, related_name="pauses_planning"
    )
    nom = models.CharField(max_length=80)
    debut = models.DateTimeField()
    duree_minutes = models.PositiveSmallIntegerField()
    est_active = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["edition", "debut"], name="unique_pause_par_edition_debut"
            ),
        ]

    def clean(self) -> None:
        erreurs = {}
        if self.duree_minutes <= 0:
            erreurs["duree_minutes"] = "La durée doit être strictement positive."

        # règle simple et claire : la pause doit tomber sur un multiple de la durée de créneau
        slot = getattr(self.edition, "duree_creneau_minutes", 15)
        if self.debut and (self.debut.minute % slot) != 0:
            erreurs["debut"] = f"La pause doit commencer sur un multiple de {slot} minutes."

        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
