from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.models import Edition
from planning.models import Terrain
from api_public.serializers.terrains import TerrainPublicSerializer
from api_public.openapi.terrains import schema_terrains_public


@schema_terrains_public
class TerrainViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = TerrainPublicSerializer
    authentication_classes = []
    queryset = Terrain.objects.select_related("edition").order_by(
        "edition__date_evenement", "ordre", "id"
    )

    def get_queryset(self):
        qs = super().get_queryset()

        edition = self.request.query_params.get("edition")
        if edition:
            qs = qs.filter(edition_id=edition)
        else:
            last = Edition.objects.order_by("-date_evenement").first()
            if last:
                qs = qs.filter(edition=last)
            else:
                return qs.none()

        # public: par défaut ne montrer que les terrains actifs
        actif = self.request.query_params.get("actif")
        if actif is None or actif == "1" or actif.lower() == "true":
            qs = qs.filter(est_actif=True)

        return qs
