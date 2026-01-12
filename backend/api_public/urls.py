from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api_public.views.planning import PlanningViewSet
from api_public.views.resultats import ResultatsViewSet


router = DefaultRouter()
router.register("planning", PlanningViewSet, basename="public-planning")
router.register("resultats", ResultatsViewSet, basename="public-resultats")

urlpatterns = [
    path("", include(router.urls)),
]
