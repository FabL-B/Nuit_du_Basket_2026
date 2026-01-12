from rest_framework import serializers

class PlanningGlobalInputSerializer(serializers.Serializer):
    phase1_id = serializers.IntegerField()
    phase2_id = serializers.IntegerField(required=False, allow_null=True)
    phase_finale_id = serializers.IntegerField(required=False, allow_null=True)
    heure_debut_concours = serializers.TimeField(required=False, allow_null=True)
    duree_concours_minutes = serializers.IntegerField(required=False, allow_null=True, min_value=1)
