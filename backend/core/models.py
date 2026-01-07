from django.db import models
from django.utils import timezone


class Edition(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    date_evenement = models.DateField(unique=True)

    # défaut 14:00, modifiable
    heure_debut = models.TimeField(
        default=timezone.datetime.strptime("14:00", "%H:%M").time()
    )

    # 1 créneau = 15 min (10 match + 5 pause)
    duree_creneau_minutes = models.PositiveSmallIntegerField(default=15)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Édition"
        verbose_name_plural = "Éditions"

    def __str__(self) -> str:
        return f"{self.nom} ({self.date_evenement})"
