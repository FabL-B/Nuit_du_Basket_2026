from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Edition
from api_public.serializers.editions import EditionPublicSerializer
from api_public.openapi.editions import schema_editions_public


@schema_editions_public
class EditionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = EditionPublicSerializer

    queryset = Edition.objects.all().order_by("-date_evenement", "-id")

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        ed = Edition.objects.order_by("-date_evenement", "-id").first()
        if not ed:
            return Response({"detail": "Aucune édition."}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(ed).data, status=status.HTTP_200_OK)
    