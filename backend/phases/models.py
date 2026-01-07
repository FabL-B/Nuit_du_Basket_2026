from django.db import models


class TypePhaseGlobale(models.TextChoices):
    PHASE_1 = "PHASE_1", "Phase 1"
    PHASE_2 = "PHASE_2", "Phase 2"
    FINALE = "FINALE", "Finale"


class StatutPhase(models.TextChoices):
    BROUILLON = "BROUILLON", "Brouillon"
    OUVERTE = "OUVERTE", "Ouverte"
    CLOTUREE = "CLOTUREE", "Clôturée"


class BrancheSousPhase(models.TextChoices):
    AUCUNE = "AUCUNE", "Aucune"  # pour Phase 1
    CHALLENGE = "CHALLENGE", "Challenge"
    CONSOLANTE = "CONSOLANTE", "Consolante"


class PhaseGlobale(models.Model):
    edition = models.ForeignKey(
        "core.Edition",
        on_delete=models.PROTECT,
        related_name="phases_globales",
    )

    type_phase = models.CharField(max_length=20, choices=TypePhaseGlobale.choices)
    sequence = models.PositiveSmallIntegerField(default=1)
    statut = models.CharField(max_length=20, choices=StatutPhase.choices, default=StatutPhase.BROUILLON)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phase globale"
        verbose_name_plural = "Phases globales"
        constraints = [
            models.UniqueConstraint(
                fields=["edition", "type_phase", "sequence"],
                name="unique_phase_globale_par_edition_type_sequence",
            )
        ]

    def __str__(self) -> str:
        return f"{self.edition.nom} - {self.get_type_phase_display()} (#{self.sequence})"


class SousPhase(models.Model):
    phase_globale = models.ForeignKey(
        "phases.PhaseGlobale",
        on_delete=models.PROTECT,
        related_name="sous_phases",
    )
    tournoi = models.ForeignKey(
        "tournois.Tournoi",
        on_delete=models.PROTECT,
        related_name="sous_phases",
    )

    branche = models.CharField(max_length=20, choices=BrancheSousPhase.choices, default=BrancheSousPhase.AUCUNE)
    statut = models.CharField(max_length=20, choices=StatutPhase.choices, default=StatutPhase.BROUILLON)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sous-phase"
        verbose_name_plural = "Sous-phases"
        constraints = [
            models.UniqueConstraint(
                fields=["phase_globale", "tournoi", "branche"],
                name="unique_sous_phase_par_phase_globale_tournoi_branche",
            )
        ]

    def __str__(self) -> str:
        return f"{self.phase_globale} - {self.tournoi.get_code_display()} - {self.get_branche_display()}"
