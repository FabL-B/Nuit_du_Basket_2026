from rest_framework import serializers


class TournoiPublicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    libelle = serializers.CharField(allow_blank=True)
    code_display = serializers.CharField(source="get_code_display")

    edition_id = serializers.IntegerField(source="edition.id")
    date_evenement = serializers.DateField(source="edition.date_evenement")
