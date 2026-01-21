from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from inscriptions.models import Joueur
from api_admin.serializers.equipes import JoueurAdminSerializer

class JoueurAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = JoueurAdminSerializer
    queryset = Joueur.objects.select_related("equipe").order_by("-id")

    def get_queryset(self):
        qs = super().get_queryset()
        equipe = self.request.query_params.get("equipe")
        if equipe:
            qs = qs.filter(equipe_id=equipe)
        return qs
