from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.models import Edition
from api_public.serializers.editions import EditionPublicSerializer


class EditionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = EditionPublicSerializer

    queryset = Edition.objects.all().order_by("-date_evenement", "-id")
