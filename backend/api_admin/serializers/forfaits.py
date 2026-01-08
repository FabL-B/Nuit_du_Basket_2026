from rest_framework import serializers
from matchs.models import StatutMatch


class ForfaitSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(
        choices=[StatutMatch.FORFAIT_A, StatutMatch.FORFAIT_B, StatutMatch.DOUBLE_FORFAIT]
    )
