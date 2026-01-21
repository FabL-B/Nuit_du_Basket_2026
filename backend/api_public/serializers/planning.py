from rest_framework import serializers
from datetime import timedelta
from django.utils import timezone

from matchs.models import Score, StatutMatch


class PlanningPublicSerializer(serializers.Serializer):
    match_id = serializers.IntegerField(source="id")
    debut = serializers.DateTimeField(source="creneau.debut")

    terrain_id = serializers.IntegerField(source="terrain.id")
    terrain = serializers.CharField(source="terrain.nom")

    tournoi = serializers.CharField(source="sous_phase.tournoi.code")
    phase = serializers.CharField(source="phase_globale.type_phase")

    groupe_id = serializers.IntegerField(source="groupe.id", allow_null=True)
    groupe_code = serializers.CharField(source="groupe.code", allow_null=True)

    equipe_a_id = serializers.IntegerField(source="equipe_a.id")
    equipe_a = serializers.CharField(source="equipe_a.nom")
    equipe_b_id = serializers.IntegerField(source="equipe_b.id")
    equipe_b = serializers.CharField(source="equipe_b.nom")

    statut = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    def get_score(self, obj):
        try:
            score = obj.score
        except Score.DoesNotExist:
            return None
        return {
            "points_a": score.points_a, 
            "points_b": score.points_b, 
            "valide_le": score.valide_le,
        }

    def get_statut(self, obj):
        now = self.context.get("now") or timezone.now()
        duree = self.context.get("duree_minutes") or getattr(obj.creneau, "duree_minutes", 15)

        debut = obj.creneau.debut
        fin = debut + timedelta(minutes=int(duree))

        if debut <= now < fin:
            return "EN_COURS"
        if now < debut:
            return "A_VENIR"
        return "TERMINE"
