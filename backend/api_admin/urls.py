from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api_admin.views.editions import EditionViewSet
from api_admin.views.phases import PhaseGlobaleViewSet
from api_admin.views.tournois import TournoiViewSet
from api_admin.views.groupes import GroupeViewSet
from api_admin.views.matchs import MatchViewSet
from api_admin.views.sous_phases import SousPhaseViewSet


router = DefaultRouter()
router.register("editions", EditionViewSet, basename="edition")
router.register("phases-globales", PhaseGlobaleViewSet, basename="phaseglobale")
router.register("tournois", TournoiViewSet, basename="tournoi")
router.register("groupes", GroupeViewSet, basename="groupe")
router.register("matchs", MatchViewSet, basename="match")
router.register("sous-phases", SousPhaseViewSet, basename="sousphase")

urlpatterns = [
    path("", include(router.urls)),
]
