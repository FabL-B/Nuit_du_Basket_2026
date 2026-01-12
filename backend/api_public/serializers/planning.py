from rest_framework import serializers


class PlanningPublicSerializer(serializers.Serializer):
    match_id = serializers.IntegerField(source="id")
    debut = serializers.DateTimeField(source="creneau.debut")
    terrain = serializers.CharField(source="terrain.nom")

    tournoi = serializers.CharField(source="sous_phase.tournoi.code")
    phase = serializers.CharField(source="phase_globale.type_phase")
    groupe = serializers.CharField(source="groupe.nom", allow_null=True)

    equipe_a = serializers.CharField(source="equipe_a.nom")
    equipe_b = serializers.CharField(source="equipe_b.nom")
    score = serializers.SerializerMethodField()

    def get_score(self, obj):
        try:
            score = obj.score
        except Exception:
            score = None

        if score:
            return {"points_a": score.points_a, "points_b": score.points_b}
        return None
