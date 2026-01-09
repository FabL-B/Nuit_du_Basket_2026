from drf_spectacular.utils import OpenApiResponse


TAG_EDITIONS = "Éditions"
TAG_TOURNOIS = "Tournois"
TAG_GROUPES = "Groupes"
TAG_MATCHS = "Matchs"
TAG_PLANNING = "Planning"
TAG_SCORES = "Scores"


REP_400 = OpenApiResponse(description="Erreur de validation métier ou données invalides.")
REP_403 = OpenApiResponse(description="Accès interdit (admin uniquement).")
REP_404 = OpenApiResponse(description="Ressource introuvable.")
