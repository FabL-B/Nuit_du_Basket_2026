from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api_public.views.planning import PlanningViewSet
from api_public.views.resultats import ResultatsViewSet
from api_public.views.tournois import TournoiViewSet
from api_public.views.groupes import GroupeViewSet


router = DefaultRouter()
router.register("planning", PlanningViewSet, basename="public-planning")
router.register("resultats", ResultatsViewSet, basename="public-resultats")
router.register("tournois", TournoiViewSet, basename="public-tournois")
router.register("groupes", GroupeViewSet, basename="public-groupes")

urlpatterns = [
    path("", include(router.urls)),
]
