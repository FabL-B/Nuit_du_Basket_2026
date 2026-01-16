from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.models import Edition
from matchs.models import Match
from api_public.serializers.planning import PlanningPublicSerializer
from api_public.openapi.planning import schema_planning_public


@schema_planning_public
class PlanningViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PlanningPublicSerializer
    authentication_classes = []
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
        .filter(creneau__isnull=False, terrain__isnull=False)
        .order_by("creneau__debut", "terrain__ordre", "id")
    )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        now = timezone.now()
        # la durée "référence" vient de l’édition filtrée (défaut dernière)
        edition_id = self.request.query_params.get("edition")
        if edition_id:
            ed = Edition.objects.filter(id=edition_id).only("duree_creneau_minutes").first()
        else:
            ed = Edition.objects.order_by("-date_evenement").only("duree_creneau_minutes").first()

        ctx["now"] = now
        ctx["duree_minutes"] = ed.duree_creneau_minutes if ed else 15
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()

        edition = self.request.query_params.get("edition")
        tournoi = (
            self.request.query_params.get("tournoi")
            or self.request.query_params.get("tournoi_code")
            or self.request.query_params.get("categorie")
        )
        terrain = self.request.query_params.get("terrain")
        groupe = self.request.query_params.get("groupe")
        phase = self.request.query_params.get("phase")
        equipe = self.request.query_params.get("equipe")
        status_q = self.request.query_params.get("status")
        limit = self.request.query_params.get("limit")

        # Edition : par défaut dernière
        if edition:
            qs = qs.filter(edition_id=edition)
            ed = Edition.objects.filter(id=edition).only("duree_creneau_minutes").first()
        else:
            last = Edition.objects.order_by("-date_evenement").first()
            if not last:
                return qs.none()
            qs = qs.filter(edition=last)
            ed = last

        if tournoi:
            qs = qs.filter(sous_phase__tournoi__code=tournoi)
        if terrain:
            qs = qs.filter(terrain_id=terrain)
        if groupe:
            qs = qs.filter(groupe_id=groupe)
        if phase:
            qs = qs.filter(phase_globale__type_phase=phase)
        if equipe:
            qs = qs.filter(Q(equipe_a_id=equipe) | Q(equipe_b_id=equipe))

        # status: en_cours / a_venir / termines
        if status_q:
            now = timezone.now()
            duree = timedelta(minutes=int(getattr(ed, "duree_creneau_minutes", 15)))

            if status_q == "en_cours":
                # debut <= now < debut + duree  <=> now - duree < debut <= now
                qs = qs.filter(creneau__debut__lte=now, creneau__debut__gt=now - duree)
            elif status_q == "a_venir":
                qs = qs.filter(creneau__debut__gt=now)
            elif status_q in ("termines", "termine"):
                qs = qs.filter(creneau__debut__lte=now - duree)
            else:
                # status inconnu => 400 serait plus strict, mais côté public on ignore ou renvoie vide.
                qs = qs.none()

        # limit
        if limit:
            try:
                n = int(limit)
                if n > 0:
                    qs = qs[:n]
            except (TypeError, ValueError):
                pass

        return qs
