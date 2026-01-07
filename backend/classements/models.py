from django.db import models


class Classement(models.Model):
    groupe = models.ForeignKey("groupes.Groupe", on_delete=models.PROTECT, related_name="classements")
    equipe = models.ForeignKey("inscriptions.Equipe", on_delete=models.PROTECT, related_name="classements")

    joues = models.PositiveSmallIntegerField(default=0)
    gagnes = models.PositiveSmallIntegerField(default=0)
    perdus = models.PositiveSmallIntegerField(default=0)
    egalites = models.PositiveSmallIntegerField(default=0)

    points_marques = models.PositiveSmallIntegerField(default=0)
    points_encaisses = models.PositiveSmallIntegerField(default=0)
    difference = models.SmallIntegerField(default=0)

    points_classement = models.SmallIntegerField(default=0)  # Victoire=3, Egalité=2, Défaite=1, Forfait=0
    maj_le = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["groupe", "equipe"], name="unique_classement_par_groupe_equipe")
        ]

    def __str__(self) -> str:
        return f"{self.groupe.code} - {self.equipe.nom}"
