from rest_framework import serializers

from matchs.models import Match


class MatchSerializer(serializers.ModelSerializer):
    equipe_a_nom = serializers.CharField(source="equipe_a.nom", read_only=True)
    equipe_b_nom = serializers.CharField(source="equipe_b.nom", read_only=True)

    equipe_a_affichage = serializers.SerializerMethodField()
    equipe_b_affichage = serializers.SerializerMethodField()

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
            "libelle_equipe_a",
            "equipe_a_affichage",
            "equipe_b",
            "equipe_b_nom",
            "libelle_equipe_b",
            "equipe_b_affichage",
            "vainqueur",
            "creneau",
            "creneau_index",
            "terrain",
            "terrain_nom",
            "terrain_type",
            "statut",
            "tour_finale",
            "numero_tour",
            "cree_le",
            "modifie_le",
        ]
        read_only_fields = ["id", "cree_le", "modifie_le"]

    def get_equipe_a_affichage(self, obj):
        if obj.equipe_a:
            return obj.equipe_a.nom
        return obj.libelle_equipe_a

    def get_equipe_b_affichage(self, obj):
        if obj.equipe_b:
            return obj.equipe_b.nom
        return obj.libelle_equipe_b

    def validate(self, attrs):
        equipe_a = attrs.get("equipe_a", getattr(self.instance, "equipe_a", None))
        equipe_b = attrs.get("equipe_b", getattr(self.instance, "equipe_b", None))
        libelle_equipe_a = attrs.get(
            "libelle_equipe_a",
            getattr(self.instance, "libelle_equipe_a", ""),
        )
        libelle_equipe_b = attrs.get(
            "libelle_equipe_b",
            getattr(self.instance, "libelle_equipe_b", ""),
        )

        if not equipe_a and not libelle_equipe_a:
            raise serializers.ValidationError(
                {"libelle_equipe_a": "Renseigne une équipe A réelle ou un libellé."}
            )

        if not equipe_b and not libelle_equipe_b:
            raise serializers.ValidationError(
                {"libelle_equipe_b": "Renseigne une équipe B réelle ou un libellé."}
            )

        return attrs
