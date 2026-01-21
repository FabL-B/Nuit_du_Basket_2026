from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from core.models import Edition
from groupes.models import Groupe
from classements.services_tri import ordonner_classement_groupe
from api_public.serializers.groupes import (
    GroupePublicSerializer,
    GroupeDetailPublicSerializer,
)
from api_public.serializers.classements import ClassementRowPublicSerializer
from api_public.openapi.groupes import schema_groupes_public


@schema_groupes_public
class GroupeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = (
        Groupe.objects.select_related(
            "sous_phase",
            "sous_phase__phase_globale",
            "sous_phase__tournoi",
            "sous_phase__tournoi__edition",
        )
        .prefetch_related(
            "equipes",
            "equipes__equipe",
            "classements",
            "classements__equipe",
        )
        .order_by("sous_phase__tournoi__code", "sous_phase__branche", "code", "id")
    )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GroupeDetailPublicSerializer
        return GroupePublicSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        edition = self.request.query_params.get("edition")
        tournoi = (
            self.request.query_params.get("tournoi")
            or self.request.query_params.get("tournoi_code")
            or self.request.query_params.get("categorie")
        )
        phase = self.request.query_params.get("phase")
        branche = self.request.query_params.get("branche")

        # Edition par défaut : dernière
        if edition:
            qs = qs.filter(sous_phase__tournoi__edition_id=edition)
        else:
            last = Edition.objects.order_by("-date_evenement").first()
            if last:
                qs = qs.filter(sous_phase__tournoi__edition=last)
            else:
                return qs.none()

        if tournoi:
            qs = qs.filter(sous_phase__tournoi__code=tournoi)
        if phase:
            qs = qs.filter(sous_phase__phase_globale__type_phase=phase)
        if branche:
            qs = qs.filter(sous_phase__branche=branche)

        return qs

    @action(detail=True, methods=["get"], url_path="classement")
    def classement(self, request, pk=None):
        groupe = self.get_object()

        rows = ordonner_classement_groupe(groupe)

        data = []
        for idx, row in enumerate(rows, start=1):
            payload = ClassementRowPublicSerializer(row).data
            payload["rang"] = idx
            data.append(payload)

        return Response(
            {
                "groupe_id": groupe.id,
                "groupe_code": groupe.code,
                "rows": data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="classements")
    def classements(self, request):
        """
        Résumé : top N par groupe (par défaut 3) si resume=true.
        Sinon renvoie tous les groupes + classement complet (attention volume).
        """
        resume = (request.query_params.get("resume") or "").lower() in {"1", "true", "yes"}
        top = request.query_params.get("top")

        top_n = 3
        if top:
            try:
                top_n = max(1, int(top))
            except (TypeError, ValueError):
                top_n = 3

        groupes = self.get_queryset().order_by("id")

        out = []
        for g in groupes:
            rows = ordonner_classement_groupe(g)
            if resume:
                rows = rows[:top_n]

            data_rows = []
            for idx, row in enumerate(rows, start=1):
                payload = ClassementRowPublicSerializer(row).data
                payload["rang"] = idx
                data_rows.append(payload)

            out.append(
                {
                    "groupe_id": g.id,
                    "groupe_code": g.code,
                    "tournoi": g.sous_phase.tournoi.code,
                    "phase": g.sous_phase.phase_globale.type_phase,
                    "branche": g.sous_phase.branche,
                    "rows": data_rows,
                }
            )

        return Response(out, status=status.HTTP_200_OK)
