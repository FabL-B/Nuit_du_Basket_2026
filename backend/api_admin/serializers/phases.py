from rest_framework import serializers
from phases.models import PhaseGlobale


class PhaseGlobaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhaseGlobale
        fields = [
            "id",
            "edition",
            "type_phase",
            "sequence",
            "statut",
            "cree_le",
            "modifie_le",
        ]
        read_only_fields = ["id", "cree_le", "modifie_le"]
