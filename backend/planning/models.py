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
            models.UniqueConstraint(
                fields=["creneau", "terrain"],
                name="unique_slot_par_creneau_et_terrain",
            ),
            # type MATCH => match not null
            models.CheckConstraint(
                condition=(
                    models.Q(type_slot=TypeSlot.MATCH, match__isnull=False)
                    | models.Q(type_slot=TypeSlot.CONCOURS_SHOOT, match__isnull=True)
                ),
                name="check_slot_type_vs_match",
            ),
        ]
        indexes = [
            models.Index(fields=["edition", "type_slot"]),
            models.Index(fields=["edition", "phase_globale"]),
        ]

    def clean(self) -> None:
        erreurs = {}

        if self.edition_id and self.creneau_id:
            if self.creneau.edition_id != self.edition_id:
                erreurs["creneau"] = "Le créneau n'appartient pas à cette édition."

        if self.edition_id and self.terrain_id:
            if self.terrain.edition_id != self.edition_id:
                erreurs["terrain"] = "Le terrain n'appartient pas à cette édition."

        # cohérence match si présent
        if self.match_id:
            if self.edition_id and self.match.edition_id != self.edition_id:
                erreurs["match"] = "Le match n'appartient pas à cette édition."

            # meta debug doit correspondre au match si fourni
            if self.phase_globale_id and self.match.phase_globale_id != self.phase_globale_id:
                erreurs["phase_globale"] = "phase_globale incohérente avec le match."
            if self.sous_phase_id and self.match.sous_phase_id != self.sous_phase_id:
                erreurs["sous_phase"] = "sous_phase incohérente avec le match."

        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
