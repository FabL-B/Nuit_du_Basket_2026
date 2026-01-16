from rest_framework import serializers


class ResultatPublicSerializer(serializers.Serializer):
    match_id = serializers.IntegerField(source="id")
    debut = serializers.DateTimeField(source="creneau.debut")
    terrain = serializers.CharField(source="terrain.nom")

    tournoi = serializers.CharField(source="sous_phase.tournoi.code")
    phase = serializers.CharField(source="phase_globale.type_phase")
    groupe = serializers.CharField(source="groupe.code", allow_null=True)

    equipe_a = serializers.CharField(source="equipe_a.nom")
    equipe_b = serializers.CharField(source="equipe_b.nom")

    score = serializers.SerializerMethodField()
    score_valide_le = serializers.DateTimeField(source="score.valide_le", allow_null=True)

    def get_score(self, obj):
        score = getattr(obj, "score", None)
        if not score:
            return None
        return {"points_a": score.points_a, "points_b": score.points_b}
