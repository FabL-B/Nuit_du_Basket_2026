from rest_framework import serializers


class JoueurPublicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    prenom = serializers.CharField()
    nom = serializers.CharField()


class EquipePublicListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nom = serializers.CharField()

    tournoi = serializers.CharField(source="tournoi.code")
    statut = serializers.CharField()

    groupe_id = serializers.SerializerMethodField()
    groupe_code = serializers.SerializerMethodField()

    def _get_groupe(self, obj):
        # on prend le premier groupe lié dans l'édition active (simple MVP)
        ge = (
            obj.groupes.select_related(
                "groupe",
                "groupe__sous_phase",
                "groupe__sous_phase__phase_globale",
            )
            .order_by("groupe__id")
            .first()
        )
        return ge.groupe if ge else None

    def get_groupe_id(self, obj):
        g = self._get_groupe(obj)
        return g.id if g else None

    def get_groupe_code(self, obj):
        g = self._get_groupe(obj)
        return g.code if g else None


class EquipePublicDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nom = serializers.CharField()
    nom_club = serializers.CharField()
    statut = serializers.CharField()

    tournoi = serializers.CharField(source="tournoi.code")

    groupe_id = serializers.SerializerMethodField()
    groupe_code = serializers.SerializerMethodField()

    joueurs = JoueurPublicSerializer(many=True)

    def _get_groupe(self, obj):
        ge = (
            obj.groupes.select_related(
                "groupe",
                "groupe__sous_phase",
                "groupe__sous_phase__phase_globale",
            )
            .order_by("groupe__id")
            .first()
        )
        return ge.groupe if ge else None

    def get_groupe_id(self, obj):
        g = self._get_groupe(obj)
        return g.id if g else None

    def get_groupe_code(self, obj):
        g = self._get_groupe(obj)
        return g.code if g else None
