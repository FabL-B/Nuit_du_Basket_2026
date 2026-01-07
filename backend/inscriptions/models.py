from django.core.exceptions import ValidationError
from django.db import models


class StatutEquipe(models.TextChoices):
    BROUILLON = "BROUILLON", "Brouillon"
    VALIDEE = "VALIDEE", "Validée"
    ARCHIVEE = "ARCHIVEE", "Archivée"


class Equipe(models.Model):
    edition = models.ForeignKey(
        "core.Edition",
        on_delete=models.PROTECT,
        related_name="equipes",
    )
    tournoi = models.ForeignKey(
        "tournois.Tournoi",
        on_delete=models.PROTECT,
        related_name="equipes",
    )

    nom = models.CharField(max_length=80)
    nom_club = models.CharField(max_length=120, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=StatutEquipe.choices,
        default=StatutEquipe.BROUILLON,
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Équipe"
        verbose_name_plural = "Équipes"
        constraints = [
            models.UniqueConstraint(
                fields=["edition", "nom"],
                name="unique_nom_equipe_par_edition",
            )
        ]

    def __str__(self) -> str:
        return f"{self.nom} ({self.edition.nom} - {self.tournoi.get_code_display()})"

    def clean(self) -> None:
        """
        Règle métier: une équipe est liée à une édition ET un tournoi de cette même édition.
        """
        if self.tournoi_id and self.edition_id and self.tournoi.edition_id != self.edition_id:
            raise ValidationError("Le tournoi choisi n'appartient pas à la même édition que l'équipe.")


class Joueur(models.Model):
    equipe = models.ForeignKey(
        "inscriptions.Equipe",
        on_delete=models.CASCADE,
        related_name="joueurs",
    )

    prenom = models.CharField(max_length=60)
    nom = models.CharField(max_length=60)

    date_naissance = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=32, blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Joueur"
        verbose_name_plural = "Joueurs"

    def __str__(self) -> str:
        return f"{self.prenom} {self.nom}"
