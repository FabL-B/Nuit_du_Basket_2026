from rest_framework import serializers


class TerrainPublicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nom = serializers.CharField()
    ordre = serializers.IntegerField()
    est_actif = serializers.BooleanField()
    edition_id = serializers.IntegerField(source="edition.id")
