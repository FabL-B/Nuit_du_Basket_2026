from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from django.db.models import Count

from inscriptions.models import Equipe
from api_admin.serializers.equipes import EquipeAdminSerializer


class EquipeAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = EquipeAdminSerializer

    queryset = (
        Equipe.objects.select_related("edition", "tournoi")
        .annotate(nb_joueurs=Count("joueurs"))
        .order_by("-id")
    )

    def get_queryset(self):
        qs = super().get_queryset()
        edition = self.request.query_params.get("edition")
        categorie = (
            self.request.query_params.get("categorie")
            or self.request.query_params.get("tournoi")
            or self.request.query_params.get("tournoi_code")
        )

        if edition:
            qs = qs.filter(edition_id=edition)
        if categorie:
            qs = qs.filter(tournoi__code=categorie)

        return qs
