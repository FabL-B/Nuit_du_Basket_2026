from django.db import models


class CodeTournoi(models.TextChoices):
    ROOKIE = "ROOKIE", "Rookie"
    LOISIR = "LOISIR", "Loisir"
    COMPETITEUR = "COMPETITEUR", "Compétiteur"


class Tournoi(models.Model):
    edition = models.ForeignKey(
        "core.Edition",
        on_delete=models.PROTECT,
        related_name="tournois",
    )

    code = models.CharField(max_length=20, choices=CodeTournoi.choices)
    libelle = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name = "Tournoi"
        verbose_name_plural = "Tournois"
        constraints = [
            models.UniqueConstraint(
                fields=["edition", "code"],
                name="unique_tournoi_par_edition_et_code",
            )
        ]

    def __str__(self) -> str:
        return f"{self.edition.nom} - {self.get_code_display()}"
