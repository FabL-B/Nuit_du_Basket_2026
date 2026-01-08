from rest_framework import serializers

from tournois.models import Tournoi


class TournoiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournoi
        fields = [
            "id",
            "edition",
            "code",
            "libelle",
        ]
        read_only_fields = ["id"]
