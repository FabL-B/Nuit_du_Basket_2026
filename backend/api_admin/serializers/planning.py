from rest_framework import serializers


class SwapPlanningSerializer(serializers.Serializer):
    match_a_id = serializers.IntegerField(min_value=1)
    match_b_id = serializers.IntegerField(min_value=1)
