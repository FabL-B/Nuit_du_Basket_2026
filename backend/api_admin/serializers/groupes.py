from rest_framework import serializers

from groupes.models import Groupe, GroupeEquipe


class GroupeEquipeSerializer(serializers.ModelSerializer):
    equipe_nom = serializers.CharField(source="equipe.nom", read_only=True)
    equipe_id = serializers.IntegerField(source="equipe.id", read_only=True)

    class Meta:
        model = GroupeEquipe
        fields = ["id", "equipe_id", "equipe_nom", "seed"]


class GroupeSerializer(serializers.ModelSerializer):
    sous_phase_id = serializers.IntegerField(source="sous_phase.id", read_only=True)
    phase_globale_id = serializers.IntegerField(source="sous_phase.phase_globale_id", read_only=True)
    tournoi_id = serializers.IntegerField(source="sous_phase.tournoi_id", read_only=True)
    branche = serializers.CharField(source="sous_phase.branche", read_only=True)
    equipes = GroupeEquipeSerializer(many=True, read_only=True)

    class Meta:
        model = Groupe
        fields = [
            "id",
            "code",
            "sous_phase",
            "sous_phase_id",
            "phase_globale_id",
            "tournoi_id",
            "branche",
            "cree_le",
            "modifie_le",
            "equipes",
        ]
        read_only_fields = ["id", "cree_le", "modifie_le", "equipes"]
