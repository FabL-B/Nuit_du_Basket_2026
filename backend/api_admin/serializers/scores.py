from rest_framework import serializers


class SaisieScoreSerializer(serializers.Serializer):
    points_a = serializers.IntegerField(min_value=0)
    points_b = serializers.IntegerField(min_value=0)
