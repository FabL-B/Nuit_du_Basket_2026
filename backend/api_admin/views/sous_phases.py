from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from phases.models import SousPhase
from groupes.services_phase1 import generer_groupes_phase1_pour_sous_phase, ErreurGenerationGroupes
from api_admin.serializers.sous_phases import SousPhaseSerializer
from api_admin.openapi.sous_phases import schema_sous_phases_admin


@schema_sous_phases_admin
class SousPhaseViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = SousPhaseSerializer
    permission_classes = [IsAdminUser]
    queryset = SousPhase.objects.all().select_related("phase_globale", "tournoi").order_by("-id")
    # serializer_class = SousPhaseSerializer  # si tu en as déjà un, sinon on peut laisser plus tard

    @action(detail=True, methods=["post"], url_path="generer-groupes-phase1")
    def generer_groupes_phase1(self, request, pk=None):
        sous_phase = self.get_object()

        try:
            resume = generer_groupes_phase1_pour_sous_phase(sous_phase)
        except ErreurGenerationGroupes as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # On essaye d'être robuste: resume peut être dataclass/namespace
        def _get(obj, name, default=None):
            return getattr(obj, name, default) if obj is not None else default

        return Response(
            {
                "created": True,
                "sous_phase_id": sous_phase.id,
                "groupes_crees": _get(resume, "groupes_crees"),
                "affectations_creees": _get(resume, "affectations_creees"),
                "detail": "Génération des groupes phase 1 terminée.",
            },
            status=status.HTTP_200_OK,
        )
