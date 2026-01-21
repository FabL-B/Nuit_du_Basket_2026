from rest_framework import serializers
from inscriptions.models import Equipe, Joueur

class JoueurAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joueur
        fields = ["id", "equipe", "prenom", "nom", "date_naissance", "email", "telephone"]

class EquipeAdminSerializer(serializers.ModelSerializer):
    nb_joueurs = serializers.IntegerField(read_only=True)

    class Meta:
        model = Equipe
        fields = ["id", "edition", "tournoi", "nom", "nom_club", "statut", "nb_joueurs", "cree_le", "modifie_le"]
