from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.models import Edition
from matchs.models import Match
from api_public.serializers.resultats import ResultatPublicSerializer
from api_public.openapi.resultats import schema_resultats_public


@schema_resultats_public
class ResultatsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = ResultatPublicSerializer

    queryset = (
        Match.objects
        .select_related(
            "edition",
            "creneau",
            "terrain",
            "phase_globale",
            "sous_phase",
            "sous_phase__tournoi",
            "groupe",
            "equipe_a",
            "equipe_b",
            "score",
        )
        # résultats = match planifié + score existant + validé
        .filter(
            creneau__isnull=False,
            terrain__isnull=False,
            score__isnull=False,
            score__valide_le__isnull=False,
            score__valide_par__isnull=False,
        )
        .order_by("-score__valide_le", "creneau__debut", "terrain__ordre", "id")
    )

    def get_queryset(self):
        qs = super().get_queryset()

        edition = self.request.query_params.get("edition")
        tournoi = (
            self.request.query_params.get("tournoi")
            or self.request.query_params.get("tournoi_code")
            or self.request.query_params.get("categorie")
        )
        groupe = self.request.query_params.get("groupe")
        phase = self.request.query_params.get("phase")
        equipe = self.request.query_params.get("equipe")
        limit = self.request.query_params.get("limit")

        # Edition : par défaut dernière
        if edition:
            qs = qs.filter(edition_id=edition)
        else:
            last = Edition.objects.order_by("-date_evenement").first()
            if last:
                qs = qs.filter(edition=last)
            else:
                return qs.none()

        if tournoi:
            qs = qs.filter(sous_phase__tournoi__code=tournoi)
        if groupe:
            qs = qs.filter(groupe_id=groupe)
        if phase:
            qs = qs.filter(phase_globale__type_phase=phase)
        if equipe:
            qs = qs.filter(Q(equipe_a_id=equipe) | Q(equipe_b_id=equipe))

        if limit:
            try:
                n = int(limit)
                if n > 0:
                    qs = qs[:n]
            except (TypeError, ValueError):
                pass

        return qs
