from rest_framework import serializers


class EditionPublicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nom = serializers.CharField()
    date_evenement = serializers.DateField()
