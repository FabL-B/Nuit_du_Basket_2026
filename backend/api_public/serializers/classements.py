from rest_framework import serializers


class ClassementRowPublicSerializer(serializers.Serializer):
    equipe_id = serializers.IntegerField(source="equipe.id")
    equipe = serializers.CharField(source="equipe.nom")

    joues = serializers.IntegerField()
    gagnes = serializers.IntegerField()
    perdus = serializers.IntegerField()
    egalites = serializers.IntegerField()

    points_marques = serializers.IntegerField()
    points_encaisses = serializers.IntegerField()
    difference = serializers.IntegerField()

    points = serializers.IntegerField(source="points_classement")
    rang_manuel = serializers.IntegerField(allow_null=True)
