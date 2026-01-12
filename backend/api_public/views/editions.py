from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.models import Edition
from api_public.serializers.editions import EditionPublicSerializer
from api_public.openapi.editions import schema_editions_public


@schema_editions_public
class EditionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = EditionPublicSerializer

    queryset = Edition.objects.all().order_by("-date_evenement", "-id")
