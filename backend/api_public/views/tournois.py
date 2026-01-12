from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.models import Edition
from tournois.models import Tournoi
from api_public.serializers.tournois import TournoiPublicSerializer


class TournoiViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = TournoiPublicSerializer

    queryset = Tournoi.objects.select_related("edition").order_by("edition__date_evenement", "code")

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

        return qs
