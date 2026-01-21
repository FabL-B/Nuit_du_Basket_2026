from rest_framework import serializers


class Phase2GenererInputSerializer(serializers.Serializer):
    # { "ROOKIE": "CHALLENGE", "LOISIR": "CONSOLANTE", ... }
    decision_impair = serializers.DictField(
        child=serializers.ChoiceField(choices=["CHALLENGE", "CONSOLANTE"]),
        required=False,
    )
