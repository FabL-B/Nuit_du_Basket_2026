from rest_framework import serializers

from core.models import Edition


class EditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edition
        fields = [
            "id",
            "nom",
            "date_evenement",
            "heure_debut",
            "duree_creneau_minutes",
            "cree_le",
            "modifie_le",
        ]
        read_only_fields = ["id", "cree_le", "modifie_le"]
