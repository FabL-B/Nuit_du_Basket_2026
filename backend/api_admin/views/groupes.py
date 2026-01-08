from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from groupes.models import Groupe, GroupeEquipe
from api_admin.serializers.groupes import GroupeSerializer

from groupes.services_swap import swap_equipes_entre_groupes, ErreurSwapGroupes


class GroupeViewSet(viewsets.ModelViewSet):
    queryset = (
        Groupe.objects.all()
        .select_related("sous_phase", "sous_phase__phase_globale", "sous_phase__tournoi")
        .prefetch_related("equipes", "equipes__equipe")
        .order_by("id")
    )
    serializer_class = GroupeSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()

        # filtres GET simples
        phase_globale_id = self.request.query_params.get("phase_globale")
        sous_phase_id = self.request.query_params.get("sous_phase")
        tournoi_id = self.request.query_params.get("tournoi")

        if phase_globale_id:
            qs = qs.filter(sous_phase__phase_globale_id=phase_globale_id)
        if sous_phase_id:
            qs = qs.filter(sous_phase_id=sous_phase_id)
        if tournoi_id:
            qs = qs.filter(sous_phase__tournoi_id=tournoi_id)

        return qs

    @action(detail=False, methods=["post"], url_path="swap-equipes")
    def swap_equipes(self, request):
        """
        Body:
        {
          "groupe_a_id": 1,
          "equipe_a_id": 10,
          "groupe_b_id": 2,
          "equipe_b_id": 11
        }
        """
        try:
            groupe_a_id = int(request.data["groupe_a_id"])
            equipe_a_id = int(request.data["equipe_a_id"])
            groupe_b_id = int(request.data["groupe_b_id"])
            equipe_b_id = int(request.data["equipe_b_id"])
        except (KeyError, TypeError, ValueError):
            return Response({"detail": "Payload invalide."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ge_a = GroupeEquipe.objects.select_related("groupe", "groupe__sous_phase").get(
                groupe_id=groupe_a_id, equipe_id=equipe_a_id
            )
            ge_b = GroupeEquipe.objects.select_related("groupe", "groupe__sous_phase").get(
                groupe_id=groupe_b_id, equipe_id=equipe_b_id
            )
        except GroupeEquipe.DoesNotExist:
            return Response({"detail": "Affectation introuvable (groupe/equipe)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            swap_equipes_entre_groupes(ge_a, ge_b)
        except ErreurSwapGroupes as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Swap effectué."}, status=status.HTTP_200_OK)
