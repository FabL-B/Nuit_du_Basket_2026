from rest_framework import serializers


class SwapPlanningSerializer(serializers.Serializer):
    match_a_id = serializers.IntegerField(min_value=1)
    match_b_id = serializers.IntegerField(min_value=1)

class PlanningAdminRowSerializer(serializers.Serializer):
    match_id = serializers.IntegerField(source="id")
    debut = serializers.DateTimeField(source="creneau.debut", allow_null=True)
    terrain = serializers.CharField(source="terrain.nom", allow_null=True)
    tournoi = serializers.CharField(source="sous_phase.tournoi.code", allow_null=True)
    phase = serializers.CharField(source="phase_globale.type_phase")
    groupe_code = serializers.CharField(source="groupe.code", allow_null=True)
    equipe_a = serializers.CharField(source="equipe_a.nom")
    equipe_b = serializers.CharField(source="equipe_b.nom")
    statut_match = serializers.CharField(source="statut")