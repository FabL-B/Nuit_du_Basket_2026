from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from phases.models import PhaseGlobale, SousPhase
from api_admin.serializers.phases import PhaseGlobaleSerializer

from phases.services.sous_phases import (
    generer_sous_phases_pour_phase_globale,
    ErreurGenerationSousPhases,
)
from phases.services.cloture import cloturer_phase_globale, ErreurCloturePhase
from phases.services.phases2 import previsualiser_phase2_depuis_phase1, ErreurGenerationPhase2
from matchs.services_generation import generer_matchs_pour_phase_globale, ErreurGenerationMatchs
from planning.services_planning import (
    generer_planning_phase_globale,
    ErreurGenerationPlanning,
)


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
                    p.__dict__ if hasattr(p, "__dict__") else p
                    for p in getattr(preview, "propositions", [])
                ],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="generer-matchs")
    def generer_matchs(self, request, pk=None):
        phase = self.get_object()
        try:
            resume = generer_matchs_pour_phase_globale(phase)
        except ErreurGenerationMatchs as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "phase_id": phase.id,
                "matchs_crees": getattr(resume, "matchs_crees", None),
                "detail": "Génération des matchs terminée.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="generer-planning")
    def generer_planning(self, request, pk=None):
        phase = self.get_object()

        try:
            resume = generer_planning_phase_globale(phase)
        except ErreurGenerationPlanning as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "phase_id": phase.id,
                "matchs_planifies": resume.matchs_planifies,
                "creneaux_crees": resume.creneaux_utilises,
                "detail": "Planning généré avec succès.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="generer-sous-phases")
    def generer_sous_phases(self, request, pk=None):
        phase_globale = self.get_object()

        try:
            sous_phases = generer_sous_phases_pour_phase_globale(phase_globale)
        except ErreurGenerationSousPhases as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "created": True,
                "sous_phases_creees": len(sous_phases),
                "sous_phase_ids": [sp.id for sp in sous_phases],
                "phase_globale_id": phase_globale.id,
            },
            status=status.HTTP_200_OK,
        )
