from django.core.exceptions import ValidationError

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser

from api_admin.openapi.matchs import (
    schema_matchs_viewset,
    schema_generer_feuille,
    schema_saisir_score,
    schema_valider_score,
    schema_swap_planning,
    schema_forfait,
)
from api_admin.serializers.matchs import MatchSerializer
from api_admin.serializers.feuilles import MatchSheetSerializer
from api_admin.serializers.scores import SaisieScoreSerializer
from api_admin.serializers.planning import SwapPlanningSerializer
from api_admin.serializers.forfaits import ForfaitSerializer

from matchs.models import Match, MatchSheet, Score
from matchs.services_scores import valider_score, ErreurScore
from matchs.services_forfaits import declarer_forfait, ErreurForfait
from planning.services_editions import swap_planning_matchs, ErreurEditionPlanning


@schema_matchs_viewset
class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = MatchSerializer

    queryset = (
        Match.objects.all()
        .select_related(
            "edition",
            "phase_globale",
            "sous_phase",
            "sous_phase__tournoi",
            "groupe",
            "equipe_a",
            "equipe_b",
            "creneau",
            "terrain",
        )
        .order_by("id")
    )

    def get_queryset(self):
        qs = super().get_queryset()

        # filtres
        edition_id = self.request.query_params.get("edition")
        phase_globale_id = self.request.query_params.get("phase_globale")
        sous_phase_id = self.request.query_params.get("sous_phase")
        tournoi_code = self.request.query_params.get("tournoi_code")
        groupe_id = self.request.query_params.get("groupe")
        terrain_id = self.request.query_params.get("terrain")
        creneau_id = self.request.query_params.get("creneau")
        statut = self.request.query_params.get("statut")

        if edition_id:
            qs = qs.filter(edition_id=edition_id)
        if phase_globale_id:
            qs = qs.filter(phase_globale_id=phase_globale_id)
        if sous_phase_id:
            qs = qs.filter(sous_phase_id=sous_phase_id)
        if tournoi_code:
            qs = qs.filter(sous_phase__tournoi__code=tournoi_code)
        if groupe_id:
            qs = qs.filter(groupe_id=groupe_id)
        if terrain_id:
            qs = qs.filter(terrain_id=terrain_id)
        if creneau_id:
            qs = qs.filter(creneau_id=creneau_id)
        if statut:
            qs = qs.filter(statut=statut)

        return qs

    @schema_generer_feuille
    @action(detail=True, methods=["post"], url_path="feuille")
    def generer_feuille(self, request, pk=None):
        match = self.get_object()

        feuille, created = MatchSheet.objects.get_or_create(match=match)

        serializer = MatchSheetSerializer(feuille)
        return Response(
            {
                "created": created,
                "feuille": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @schema_saisir_score
    @action(detail=True, methods=["post"], url_path="score")
    def saisir_score(self, request, pk=None):
        match = self.get_object()

        serializer = SaisieScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        points_a = serializer.validated_data["points_a"]
        points_b = serializer.validated_data["points_b"]

        score, _ = Score.objects.get_or_create(
            match=match,
            defaults={"points_a": points_a, "points_b": points_b},
        )

        if score.pk and (score.points_a != points_a or score.points_b != points_b):
            score.points_a = points_a
            score.points_b = points_b

        try:
            score.full_clean()
            score.save()
        except ValidationError as e:
            return Response(
                {"detail": e.message_dict if hasattr(e, "message_dict") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "match_id": match.id,
                "score_id": score.id,
                "points_a": score.points_a,
                "points_b": score.points_b,
                "valide_le": score.valide_le,
            },
            status=status.HTTP_200_OK,
        )

    @schema_valider_score
    @action(detail=True, methods=["post"], url_path="score/valider")
    def valider_score(self, request, pk=None):
        match = self.get_object()

        try:
            score = valider_score(match, request.user)
        except (ErreurScore, ValidationError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "match_id": match.id,
                "score_id": score.id,
                "valide_le": score.valide_le,
                "valide_par": score.valide_par_id,
                "statut_match": match.statut,
                "detail": "Score validé.",
            },
            status=status.HTTP_200_OK,
        )

    @schema_swap_planning
    @action(detail=False, methods=["post"], url_path="swap-planning")
    def swap_planning(self, request):
        serializer = SwapPlanningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        match_a = Match.objects.get(pk=serializer.validated_data["match_a_id"])
        match_b = Match.objects.get(pk=serializer.validated_data["match_b_id"])

        try:
            resume = swap_planning_matchs(match_a, match_b)
        except ErreurEditionPlanning as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "detail": "Swap planning effectué.",
                "match_a_id": resume.match_a_id,
                "match_b_id": resume.match_b_id,
            },
            status=status.HTTP_200_OK,
        )

    @schema_forfait
    @action(detail=True, methods=["post"], url_path="forfait")
    def forfait(self, request, pk=None):
        match = self.get_object()

        serializer = ForfaitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        statut = serializer.validated_data["statut"]

        try:
            resume = declarer_forfait(match, statut)
        except ErreurForfait as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "match_id": resume.match_id,
                "statut_match": resume.statut_match,
                "detail": "Forfait enregistré.",
            },
            status=status.HTTP_200_OK,
        )
