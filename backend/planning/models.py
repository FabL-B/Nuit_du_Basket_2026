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


class TypeSlot(models.TextChoices):
    MATCH = "MATCH", "Match"
    CONCOURS_SHOOT = "CONCOURS_SHOOT", "Concours de shoot"


class PlanningSlot(models.Model):
    """
    Un slot = l'occupation d'un terrain sur un créneau.

    - type=MATCH => match obligatoire
    - type=CONCOURS_SHOOT => match interdit (pause globale)
    """

    edition = models.ForeignKey(
        "core.Edition",
        on_delete=models.PROTECT,
        related_name="planning_slots",
    )
    creneau = models.ForeignKey(
        "planning.Creneau",
        on_delete=models.CASCADE,
        related_name="slots",
    )
    terrain = models.ForeignKey(
        "planning.Terrain",
        on_delete=models.PROTECT,
        related_name="slots",
    )

    type_slot = models.CharField(max_length=32, choices=TypeSlot.choices)

    match = models.OneToOneField(
        "matchs.Match",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="planning_slot",
    )

    # Méta “debug/filtre” (optionnel mais très utile)
    phase_globale = models.ForeignKey(
        "phases.PhaseGlobale",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="planning_slots",
    )
    sous_phase = models.ForeignKey(
        "phases.SousPhase",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="planning_slots",
    )

    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Un terrain ne peut avoir qu'un slot sur un créneau
            models.UniqueConstraint(
                fields=["creneau", "terrain"],
                name="unique_slot_par_creneau_et_terrain",
            ),
            # Optionnel mais fort : empêcher slots cross-édition incohérents
            models.UniqueConstraint(
                fields=["edition", "creneau", "terrain"],
                name="unique_slot_par_edition_creneau_terrain",
            ),
        ]

    def clean(self) -> None:
        erreurs = {}

        # Cohérence édition
        if self.creneau_id and self.edition_id:
            if self.creneau.edition_id != self.edition_id:
                erreurs["creneau"] = "Le créneau n'appartient pas à cette édition."

        if self.terrain_id and self.edition_id:
            if self.terrain.edition_id != self.edition_id:
                erreurs["terrain"] = "Le terrain n'appartient pas à cette édition."

        # Règles type_slot <-> match
        if self.type_slot == TypeSlot.MATCH:
            if self.match_id is None:
                erreurs["match"] = "Un slot de type MATCH doit référencer un match."
        elif self.type_slot == TypeSlot.CONCOURS_SHOOT:
            if self.match_id is not None:
                erreurs["match"] = "Un slot CONCOURS_SHOOT ne doit pas référencer de match."
        else:
            erreurs["type_slot"] = "Type de slot invalide."

        # Cohérence match si présent
        if self.match_id and self.edition_id:
            if self.match.edition_id != self.edition_id:
                erreurs["match"] = "Le match n'appartient pas à cette édition."

        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
