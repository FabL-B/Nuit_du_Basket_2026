from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from tournois.models import Tournoi
from api_admin.serializers.tournois import TournoiSerializer


class TournoiViewSet(viewsets.ModelViewSet):
    queryset = Tournoi.objects.all().order_by("edition__date_evenement", "code")
    serializer_class = TournoiSerializer
    permission_classes = [IsAdminUser]
