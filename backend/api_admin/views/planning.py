from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

from matchs.models import Match
from core.models import Edition
from planning.models import PausePlanning
from api_admin.serializers.planning import PlanningAdminRowSerializer
from planning.services_global import generer_planning_global, ErreurPlanningGlobal
from planning.services_planning import generer_planning_phase_globale, ErreurGenerationPlanning
from phases.models import PhaseGlobale

class PlanningAdminViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = PlanningAdminRowSerializer

    queryset = (
        Match.objects
        .select_related(
            "edition","creneau","terrain","phase_globale","sous_phase","sous_phase__tournoi","groupe","equipe_a","equipe_b","score",
        )
        .order_by("creneau__debut", "terrain__ordre", "id")
    )

    def get_queryset(self):
        qs = super().get_queryset()
        edition = self.request.query_params.get("edition")
        categorie = self.request.query_params.get("categorie") or self.request.query_params.get("tournoi") or self.request.query_params.get("tournoi_code")
        phase = self.request.query_params.get("phase")

        if edition:
            qs = qs.filter(edition_id=edition)
        else:
            last = Edition.objects.order_by("-date_evenement").first()
            if not last:
                return qs.none()
            qs = qs.filter(edition=last)

        if categorie:
            qs = qs.filter(sous_phase__tournoi__code=categorie)
        if phase:
            qs = qs.filter(phase_globale__type_phase=phase)

        return qs

    @action(detail=False, methods=["post"], url_path="generer")
    def generer(self, request):
        """
        Wrapper front:
        - soit planning global via edition + phase1/2/finale
        - soit planning d'une phase via phase_globale_id
        """
        edition_id = request.data.get("edition_id")
        phase_globale_id = request.data.get("phase_globale_id")

        if phase_globale_id:
            phase = PhaseGlobale.objects.get(id=phase_globale_id)
            try:
                res = generer_planning_phase_globale(phase)
            except ErreurGenerationPlanning as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"phase_id": phase.id, "matchs_planifies": res.matchs_planifies}, status=status.HTTP_200_OK)

        # planning global
        if not edition_id:
            return Response({"detail": "edition_id requis (ou phase_globale_id)."}, status=status.HTTP_400_BAD_REQUEST)

        edition = Edition.objects.get(id=edition_id)
        phase1_id = request.data.get("phase1_id")
        phase2_id = request.data.get("phase2_id")
        finale_id = request.data.get("phase_finale_id")

        if not phase1_id:
            return Response({"detail": "phase1_id requis pour planning global."}, status=status.HTTP_400_BAD_REQUEST)

        phase1 = PhaseGlobale.objects.get(id=phase1_id)
        phase2 = PhaseGlobale.objects.get(id=phase2_id) if phase2_id else None
        finale = PhaseGlobale.objects.get(id=finale_id) if finale_id else None

        try:
            resume = generer_planning_global(
                edition=edition,
                phase1=phase1,
                phase2=phase2,
                phase_finale=finale,
                heure_debut_concours=request.data.get("heure_debut_concours"),
                duree_concours_minutes=request.data.get("duree_concours_minutes"),
            )
        except ErreurPlanningGlobal as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "edition_id": edition.id,
                "phase1_matchs_planifies": resume.phase1_matchs_planifies,
                "phase2_matchs_planifies": resume.phase2_matchs_planifies,
                "finale_matchs_planifies": resume.finale_matchs_planifies,
                "pause_creee": resume.pause_creee,
                "creneaux_deplaces": resume.creneaux_deplaces,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="pause")
    def pause(self, request):
        edition_id = request.data.get("edition_id")
        nom = request.data.get("nom", "Pause")
        debut = request.data.get("debut")  # ISO datetime
        duree_minutes = request.data.get("duree_minutes")

        if not (edition_id and debut and duree_minutes):
            return Response({"detail": "edition_id, debut, duree_minutes requis."}, status=status.HTTP_400_BAD_REQUEST)

        p = PausePlanning.objects.create(
            edition_id=edition_id,
            nom=nom,
            debut=debut,
            duree_minutes=duree_minutes,
            est_active=True,
        )
        return Response({"pause_id": p.id, "detail": "Pause créée."}, status=status.HTTP_200_OK)
