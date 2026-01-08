from rest_framework import viewsets

from core.models import Edition
from api_admin.serializers.editions import EditionSerializer


class EditionViewSet(viewsets.ModelViewSet):
    queryset = Edition.objects.all().order_by("-date_evenement")
    serializer_class = EditionSerializer
