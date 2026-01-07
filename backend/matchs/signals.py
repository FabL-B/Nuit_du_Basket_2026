from django.db.models.signals import post_save
from django.dispatch import receiver

from matchs.models import Match, MatchSheet


@receiver(post_save, sender=Match)
def creer_feuille_match(sender, instance: Match, created: bool, **kwargs):
    if created:
        MatchSheet.objects.create(match=instance)
