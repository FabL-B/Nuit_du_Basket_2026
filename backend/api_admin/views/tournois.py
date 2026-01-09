from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from tournois.models import Tournoi
from api_admin.serializers.tournois import TournoiSerializer
from api_admin.openapi.tournois import schema_tournois_viewset


@schema_tournois_viewset
class TournoiViewSet(viewsets.ModelViewSet):
    queryset = Tournoi.objects.all().order_by("edition__date_evenement", "code")
    serializer_class = TournoiSerializer
    permission_classes = [IsAdminUser]
