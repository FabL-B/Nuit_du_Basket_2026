from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core.models import Edition
from phases.models import PhaseGlobale
from api_admin.serializers.editions import EditionSerializer
from api_admin.openapi.editions import schema_editions_viewset, schema_generer_planning_global
from api_admin.serializers.planning_global import PlanningGlobalInputSerializer

from planning.services_global import generer_planning_global, ErreurPlanningGlobal


@schema_editions_viewset
class EditionViewSet(viewsets.ModelViewSet):
    queryset = Edition.objects.all().order_by("-date_evenement")
    serializer_class = EditionSerializer
    permission_classes = [IsAdminUser]

    @schema_generer_planning_global
    @action(detail=True, methods=["post"], url_path="planning-global/generer")
    def generer_planning_global(self, request, pk=None):
        edition = self.get_object()

        serializer = PlanningGlobalInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phase1_id = serializer.validated_data["phase1_id"]
        phase2_id = serializer.validated_data.get("phase2_id")
        phase_finale_id = serializer.validated_data.get("phase_finale_id")
        heure_debut_concours = serializer.validated_data.get("heure_debut_concours")
        duree_concours_minutes = serializer.validated_data.get("duree_concours_minutes")

        # Récupération phases (et garde-fou: même édition)
        try:
            phase1 = PhaseGlobale.objects.get(id=phase1_id, edition=edition)
            phase2 = PhaseGlobale.objects.get(id=phase2_id, edition=edition) if phase2_id else None
            phase_finale = (
                PhaseGlobale.objects.get(id=phase_finale_id, edition=edition)
                if phase_finale_id
                else None
            )
        except PhaseGlobale.DoesNotExist:
            return Response(
                {"detail": "Phase(s) introuvable(s) pour cette édition."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            resume = generer_planning_global(
                edition=edition,
                phase1=phase1,
                phase2=phase2,
                phase_finale=phase_finale,
                heure_debut_concours=heure_debut_concours,
                duree_concours_minutes=duree_concours_minutes,
            )
        except ErreurPlanningGlobal as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # resume est sérialisable (dataclass/namespace) => dict
        data = resume.__dict__ if hasattr(resume, "__dict__") else {"resume": str(resume)}

        return Response(
            {
                "detail": "Planning global généré.",
                "edition_id": edition.id,
                "resume": data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="stats")
    def stats(self, request, pk=None):
        edition = self.get_object()
        group_by = request.query_params.get("group_by")

        equipes_qs = Equipe.objects.filter(edition=edition).exclude(statut="BROUILLON")
        joueurs_qs = Joueur.objects.filter(equipe__edition=edition).exclude(
            equipe__statut="BROUILLON"
        )

        if group_by in ("categorie", "tournoi"):
            rows = (
                equipes_qs.values("tournoi__code")
                .annotate(
                    equipes=Count("id"),
                    joueurs=Count("joueurs"),
                )
                .order_by("tournoi__code")
            )
            return Response(
                {
                    "edition_id": edition.id,
                    "group_by": "categorie",
                    "rows": list(rows),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "edition_id": edition.id,
                "equipes": equipes_qs.count(),
                "joueurs": joueurs_qs.count(),
            },
            status=status.HTTP_200_OK,
        )
