from rest_framework import serializers
from phases.models import SousPhase


class SousPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousPhase
        fields = ["id", "phase_globale", "tournoi", "branche"]
