from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from api_admin.serializers.phases import PhaseGlobaleSerializer
from api_admin.serializers.phase2 import Phase2GenererInputSerializer


def _err400_example(name: str, msg: str):
    return OpenApiExample(name, value={"detail": msg}, response_only=True, status_codes=["400"])


schema_phases_admin = extend_schema_view(
    list=extend_schema(
        tags=["Admin - Phases"],
        summary="Lister les phases globales",
        responses={200: PhaseGlobaleSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Admin - Phases"],
        summary="Détail d’une phase globale",
        responses={200: PhaseGlobaleSerializer},
    ),
    create=extend_schema(
        tags=["Admin - Phases"],
        summary="Créer une phase globale",
        responses={201: PhaseGlobaleSerializer},
    ),
    update=extend_schema(
        tags=["Admin - Phases"],
        summary="Mettre à jour une phase globale",
        responses={200: PhaseGlobaleSerializer},
    ),
    partial_update=extend_schema(
        tags=["Admin - Phases"],
        summary="Mettre à jour partiellement une phase globale",
        responses={200: PhaseGlobaleSerializer},
    ),
    destroy=extend_schema(
        tags=["Admin - Phases"],
        summary="Supprimer une phase globale",
        responses={204: OpenApiResponse(description="Supprimé.")},
    ),
    # --- Actions ---
    cloturer=extend_schema(
        tags=["Admin - Phases"],
        summary="Clôturer une phase globale",
        description="Clôture la phase et renvoie un résumé (aucun objet complexe).",
        responses={
            200: OpenApiResponse(
                description="Phase clôturée.",
                examples=[
                    OpenApiExample(
                        "Réponse cloturer",
                        value={
                            "phase_id": 12,
                            "type_phase": "PHASE_1",
                            "statut": "CLOTUREE",
                            "resume": {"exemple": "valeur"},
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Erreur métier de clôture.",
                examples=[
                    _err400_example("Clôture impossible", "La phase ne peut pas être clôturée.")
                ],
            ),
            403: OpenApiResponse(description="Non autorisé (admin requis)."),
        },
    ),
    phase2_preview=extend_schema(
        tags=["Admin - Phases"],
        summary="Prévisualiser la génération de la phase 2",
        description="Calcule un aperçu (propositions) sans créer/modifier d’objets.",
        responses={
            200: OpenApiResponse(
                description="Aperçu de la phase 2.",
                examples=[
                    OpenApiExample(
                        "Réponse phase2-preview",
                        value={
                            "phase2_id": 34,
                            "tournois_impairs": ["ROOKIE"],
                            "propositions": [{"tournoi_code": "ROOKIE", "decision": "exemple"}],
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Erreur métier de génération phase 2.",
                examples=[
                    _err400_example("Preview impossible", "Impossible de prévisualiser la phase 2.")
                ],
            ),
            403: OpenApiResponse(description="Non autorisé (admin requis)."),
        },
    ),
    generer_sous_phases=extend_schema(
        tags=["Admin - Phases"],
        summary="Générer les sous-phases d’une phase globale",
        description="Crée les sous-phases (par tournoi / branche) pour la phase globale.",
        responses={
            200: OpenApiResponse(
                description="Sous-phases générées.",
                examples=[
                    OpenApiExample(
                        "Réponse generer-sous-phases",
                        value={
                            "created": True,
                            "sous_phases_creees": 6,
                            "sous_phase_ids": [101, 102, 103],
                            "phase_globale_id": 12,
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Erreur métier de génération des sous-phases.",
                examples=[
                    _err400_example("Génération impossible", "Les sous-phases existent déjà.")
                ],
            ),
            403: OpenApiResponse(description="Non autorisé (admin requis)."),
        },
    ),
    generer_matchs=extend_schema(
        tags=["Admin - Phases"],
        summary="Générer les matchs d’une phase globale",
        description="Génère tous les matchs de la phase globale (tous groupes/tournois confondus).",
        responses={
            200: OpenApiResponse(
                description="Matchs générés.",
                examples=[
                    OpenApiExample(
                        "Réponse generer-matchs",
                        value={
                            "phase_id": 12,
                            "matchs_crees": 48,
                            "detail": "Génération des matchs terminée.",
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Erreur métier de génération des matchs.",
                examples=[
                    _err400_example("Génération impossible", "Aucun groupe pour cette phase.")
                ],
            ),
            403: OpenApiResponse(description="Non autorisé (admin requis)."),
        },
    ),
    generer_planning=extend_schema(
        tags=["Admin - Phases"],
        summary="Générer le planning d’une phase globale",
        description="Planifie les matchs de la phase globale (créneaux + terrains).",
        responses={
            200: OpenApiResponse(
                description="Planning généré.",
                examples=[
                    OpenApiExample(
                        "Réponse generer-planning",
                        value={
                            "phase_id": 12,
                            "matchs_planifies": 48,
                            "creneaux_crees": 6,
                            "detail": "Planning généré avec succès.",
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Erreur métier de génération planning.",
                examples=[
                    _err400_example("Planning impossible", "Contraintes impossibles à satisfaire.")
                ],
            ),
            403: OpenApiResponse(description="Non autorisé (admin requis)."),
        },
    ),
    phase2_generer=extend_schema(
        tags=["Admin - Phases"],
        summary="Générer la phase 2 à partir de la phase 1",
        description=(
            "Génère la phase 2 depuis une phase 1.\n"
            "Le body contient la décision à appliquer si un tournoi a un nombre impair d’équipes."
        ),
        request=Phase2GenererInputSerializer,
        responses={
            200: OpenApiResponse(
                description="Phase 2 générée.",
                examples=[
                    OpenApiExample(
                        "Réponse phase2-generer",
                        value={
                            "created": True,
                            "phase1_id": 12,
                            "phase2_id": 34,
                            "equipes_challenge": 24,
                            "equipes_consolante": 24,
                            "sous_phases_creees": 6,
                            "groupes_crees": 12,
                            "detail": "Phase 2 générée.",
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Erreur métier de génération phase 2.",
                examples=[_err400_example("Génération impossible", "Décision impair invalide.")],
            ),
            403: OpenApiResponse(description="Non autorisé (admin requis)."),
        },
        examples=[
            OpenApiExample(
                "Body phase2-generer",
                value={"decision_impair": "EXEMPLE"},
                request_only=True,
            )
        ],
    ),
)
