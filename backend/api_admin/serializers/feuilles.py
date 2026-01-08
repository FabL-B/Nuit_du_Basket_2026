from rest_framework import serializers
from matchs.models import MatchSheet


class MatchSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchSheet
        fields = [
            "id",
            "sheet_code",
            "cree_le",
        ]
        read_only_fields = fields
