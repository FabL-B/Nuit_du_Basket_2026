from django.db import models

# Create your models here.
from django.core.exceptions import ValidationError
from django.db import models


class Groupe(models.Model):
    sous_phase = models.ForeignKey(
        "phases.SousPhase",
        on_delete=models.PROTECT,
        related_name="groupes",
    )

    code = models.CharField(max_length=16)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"
        constraints = [
            models.UniqueConstraint(
                fields=["sous_phase", "code"],
                name="unique_code_groupe_par_sous_phase",
            )
        ]

    def __str__(self) -> str:
        return f"{self.sous_phase} - Groupe {self.code}"


class GroupeEquipe(models.Model):
    groupe = models.ForeignKey(
        "groupes.Groupe",
        on_delete=models.CASCADE,
        related_name="equipes",
    )
    equipe = models.ForeignKey(
        "inscriptions.Equipe",
        on_delete=models.PROTECT,
        related_name="groupes",
    )

    seed = models.PositiveSmallIntegerField(null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Équipe du groupe"
        verbose_name_plural = "Équipes du groupe"
        constraints = [
            models.UniqueConstraint(
                fields=["groupe", "equipe"],
                name="unique_equipe_par_groupe",
            ),
            models.UniqueConstraint(
                fields=["groupe", "seed"],
                condition=models.Q(seed__isnull=False),
                name="unique_seed_par_groupe_si_renseigne",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.groupe} - {self.equipe.nom}"

    def clean(self) -> None:
        """
        Règle métier:
        - l'équipe doit appartenir au même tournoi que la sous-phase du groupe
        - l'équipe doit appartenir à la même édition que la sous-phase du groupe
        """
        if not self.groupe_id or not self.equipe_id:
            return

        sous_phase = self.groupe.sous_phase
        equipe = self.equipe

        if equipe.edition_id != sous_phase.phase_globale.edition_id:
            raise ValidationError("L'équipe n'appartient pas à la même édition que ce groupe.")

        if equipe.tournoi_id != sous_phase.tournoi_id:
            raise ValidationError("L'équipe n'appartient pas au bon tournoi pour ce groupe.")

    def save(self, *args, **kwargs):
        # garantit que clean() est appliqué même si on oublie full_clean() ailleurs
        self.full_clean()
        return super().save(*args, **kwargs)
