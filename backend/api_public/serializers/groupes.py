from rest_framework import serializers


class GroupePublicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()

    phase = serializers.CharField(source="sous_phase.phase_globale.type_phase")
    branche = serializers.CharField(source="sous_phase.branche")
    tournoi = serializers.CharField(source="sous_phase.tournoi.code")


class GroupeEquipePublicSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="equipe.id")
    nom = serializers.CharField(source="equipe.nom")
    seed = serializers.IntegerField(allow_null=True)


class GroupeDetailPublicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()

    phase = serializers.CharField(source="sous_phase.phase_globale.type_phase")
    branche = serializers.CharField(source="sous_phase.branche")
    tournoi = serializers.CharField(source="sous_phase.tournoi.code")

    equipes = GroupeEquipePublicSerializer(many=True)
