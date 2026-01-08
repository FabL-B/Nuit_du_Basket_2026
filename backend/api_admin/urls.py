from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api_admin.views.editions import EditionViewSet
from api_admin.views.phases import PhaseGlobaleViewSet
from api_admin.views.tournois import TournoiViewSet


router = DefaultRouter()
router.register("editions", EditionViewSet, basename="edition")
router.register("phases-globales", PhaseGlobaleViewSet, basename="phaseglobale")
router.register("tournois", TournoiViewSet, basename="tournoi")

urlpatterns = [
    path("", include(router.urls)),
]
