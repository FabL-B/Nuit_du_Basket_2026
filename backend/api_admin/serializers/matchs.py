from rest_framework import serializers

from matchs.models import Match


class MatchSerializer(serializers.ModelSerializer):
    equipe_a_nom = serializers.CharField(source="equipe_a.nom", read_only=True)
    equipe_b_nom = serializers.CharField(source="equipe_b.nom", read_only=True)
    groupe_code = serializers.CharField(source="groupe.code", read_only=True)
    sous_phase_branche = serializers.CharField(source="sous_phase.branche", read_only=True)
    tournoi_code = serializers.CharField(source="sous_phase.tournoi.code", read_only=True)

    creneau_index = serializers.IntegerField(source="creneau.index", read_only=True)
    terrain_nom = serializers.CharField(source="terrain.nom", read_only=True)
    terrain_type = serializers.CharField(source="terrain.type_terrain", read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "edition",
            "phase_globale",
            "sous_phase",
            "groupe",
            "groupe_code",
            "tournoi_code",
            "sous_phase_branche",
            "equipe_a",
            "equipe_a_nom",
            "equipe_b",
            "equipe_b_nom",
            "creneau",
            "creneau_index",
            "terrain",
            "terrain_nom",
            "terrain_type",
            "statut",
            "cree_le",
            "modifie_le",
        ]
        read_only_fields = ["id", "cree_le", "modifie_le"]
