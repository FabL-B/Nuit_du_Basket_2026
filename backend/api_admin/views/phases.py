from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from phases.models import PhaseGlobale
from api_admin.serializers.phases import PhaseGlobaleSerializer

from phases.services_cloture import cloturer_phase_globale, ErreurCloturePhase
from phases.services_phase2 import previsualiser_phase2_depuis_phase1, ErreurGenerationPhase2


class PhaseGlobaleViewSet(viewsets.ModelViewSet):
    queryset = PhaseGlobale.objects.all().order_by("-id")
    serializer_class = PhaseGlobaleSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"], url_path="cloturer")
    def cloturer(self, request, pk=None):
        phase = self.get_object()
        try:
            resume = cloturer_phase_globale(phase)
        except ErreurCloturePhase as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # On renvoie un résumé simple (pas d’objet complexe)
        return Response(
            {
                "phase_id": phase.id,
                "type_phase": phase.type_phase,
                "statut": "CLOTUREE",
                "resume": resume.__dict__ if hasattr(resume, "__dict__") else str(resume),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="phase2-preview")
    def phase2_preview(self, request, pk=None):
        phase1 = self.get_object()
        try:
            preview = previsualiser_phase2_depuis_phase1(phase1)
        except ErreurGenerationPhase2 as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "phase2_id": preview.phase2_id,
                "tournois_impairs": getattr(preview, "tournois_impairs", []),
                "propositions": [
                    p.__dict__ if hasattr(p, "__dict__") else p for p in getattr(preview, "propositions", [])
                ],
            },
            status=status.HTTP_200_OK,
        )
