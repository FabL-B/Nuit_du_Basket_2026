from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api_public.views.planning import PlanningViewSet

router = DefaultRouter()
router.register("planning", PlanningViewSet, basename="public-planning")

urlpatterns = [
    path("", include(router.urls)),
]
