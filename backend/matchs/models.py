import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils import timezone


class StatutMatch(models.TextChoices):
    A_PLANIFIER = "A_PLANIFIER", "À planifier"
    PLANIFIE = "PLANIFIE", "Planifié"
    TERMINE = "TERMINE", "Terminé"
    FORFAIT_A = "FORFAIT_A", "Forfait équipe A"
    FORFAIT_B = "FORFAIT_B", "Forfait équipe B"
    DOUBLE_FORFAIT = "DOUBLE_FORFAIT", "Double forfait"


class Match(models.Model):
    edition = models.ForeignKey(
        "core.Edition",
        on_delete=models.PROTECT,
        related_name="matchs",
    )
    phase_globale = models.ForeignKey(
        "phases.PhaseGlobale",
        on_delete=models.PROTECT,
        related_name="matchs",
    )
    sous_phase = models.ForeignKey(
        "phases.SousPhase",
        on_delete=models.PROTECT,
        related_name="matchs",
    )
    groupe = models.ForeignKey(
        "groupes.Groupe",
        on_delete=models.PROTECT,
        related_name="matchs",
    )

    equipe_a = models.ForeignKey(
        "inscriptions.Equipe",
        on_delete=models.PROTECT,
        related_name="matchs_comme_a",
    )
    equipe_b = models.ForeignKey(
        "inscriptions.Equipe",
        on_delete=models.PROTECT,
        related_name="matchs_comme_b",
    )

    # Planification (nullable au départ)
    creneau = models.ForeignKey(
        "planning.Creneau",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matchs",
    )
    terrain = models.ForeignKey(
        "planning.Terrain",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matchs",
    )

    statut = models.CharField(
        max_length=20,
        choices=StatutMatch.choices,
        default=StatutMatch.A_PLANIFIER,
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(equipe_a=models.F("equipe_b")),
                name="match_equipes_differentes",
            ),
            # Empêcher doublon strict A/B (ordre) au niveau DB
            models.UniqueConstraint(
                fields=["groupe", "equipe_a", "equipe_b"],
                name="unique_match_par_groupe_et_paire_ordonne",
            ),
        ]

    def clean(self) -> None:
        """
        Cohérences strictes minimales :
        - edition cohérente partout
        - sous_phase cohérente avec phase_globale
        - groupe cohérent avec sous_phase
        - équipes cohérentes avec edition + tournoi de la sous_phase
        (Règle 'équipes du groupe' : contrôlée plus tard côté génération/service)
        """
        erreurs = {}

        if (
            self.phase_globale_id
            and self.edition_id
            and self.phase_globale.edition_id != self.edition_id
        ):
            erreurs["phase_globale"] = "La phase globale n'appartient pas à cette édition."

        if self.sous_phase_id:
            if self.phase_globale_id and self.sous_phase.phase_globale_id != self.phase_globale_id:
                erreurs["sous_phase"] = "La sous-phase n'appartient pas à cette phase globale."
            if self.edition_id and self.sous_phase.phase_globale.edition_id != self.edition_id:
                erreurs["sous_phase"] = "La sous-phase n'appartient pas à cette édition."

        if (
            self.groupe_id
            and self.sous_phase_id
            and self.groupe.sous_phase_id != self.sous_phase_id
        ):
            erreurs["groupe"] = "Le groupe n'appartient pas à cette sous-phase."

        # équipes : édition + tournoi
        if self.sous_phase_id:
            edition_id = self.sous_phase.phase_globale.edition_id
            tournoi_id = self.sous_phase.tournoi_id

            if self.equipe_a_id:
                if self.equipe_a.edition_id != edition_id:
                    erreurs["equipe_a"] = "L'équipe A n'appartient pas à la même édition."
                if self.equipe_a.tournoi_id != tournoi_id:
                    erreurs["equipe_a"] = "L'équipe A n'appartient pas au bon tournoi."

            if self.equipe_b_id:
                if self.equipe_b.edition_id != edition_id:
                    erreurs["equipe_b"] = "L'équipe B n'appartient pas à la même édition."
                if self.equipe_b.tournoi_id != tournoi_id:
                    erreurs["equipe_b"] = "L'équipe B n'appartient pas au bon tournoi."

        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class MatchSheet(models.Model):
    match = models.OneToOneField(
        "matchs.Match",
        on_delete=models.CASCADE,
        related_name="feuille",
    )
    sheet_code = models.CharField(max_length=36, unique=True, editable=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.sheet_code:
            self.sheet_code = str(uuid.uuid4())
        return super().save(*args, **kwargs)


class Score(models.Model):
    match = models.OneToOneField(
        "matchs.Match",
        on_delete=models.CASCADE,
        related_name="score",
    )
    points_a = models.PositiveSmallIntegerField()
    points_b = models.PositiveSmallIntegerField()

    valide_le = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="scores_valides",
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    def clean(self):
        # verrouillage : score validé => non modifiable
        if self.pk:
            ancien = Score.objects.filter(pk=self.pk).only("valide_le").first()
            if ancien and ancien.valide_le is not None:
                raise ValidationError({"valide_le": "Score déjà validé : modification interdite."})

        # Si valide_le est rempli, valide_par doit être rempli
        if self.valide_le is not None and self.valide_par_id is None:
            raise ValidationError({"valide_par": "L'utilisateur validant est obligatoire."})
