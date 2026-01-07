from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StatsPlanningEquipe:
    dernier_creneau: int | None = None
    matchs_interieur: int = 0
    matchs_exterieur: int = 0
    enchainements_1: int = 0  # back-to-back (slot-1)
    enchainements_2: int = 0  # quasi enchaînement (slot-2)

    @property
    def desequilibre_io(self) -> int:
        # valeur absolue du diff intérieur/extérieur
        return abs(self.matchs_interieur - self.matchs_exterieur)


@dataclass(frozen=True)
class MetriquesPlanning:
    nb_matchs: int
    nb_equipes: int
    nb_back_to_back: int
    nb_quasi_back_to_back: int
    desequilibre_io_total: int
    desequilibre_io_max: int


def penalite_match(
    equipe_a_id: int,
    equipe_b_id: int,
    slot_index: int,
    type_terrain: str,
    stats_by_team: dict[int, StatsPlanningEquipe],
    poids_b2b: int = 100,
    poids_quasi: int = 20,
    poids_io: int = 10,
) -> int:
    """
    Plus faible = meilleur.
    - gros malus si back-to-back
    - malus léger si slot-2 (tendance à enchaîner)
    - malus selon déséquilibre intérieur/extérieur (favorise compenser)
    """
    pen = 0
    for tid in (equipe_a_id, equipe_b_id):
        st = stats_by_team.setdefault(tid, StatsPlanningEquipe())
        if st.dernier_creneau is not None:
            if st.dernier_creneau == slot_index - 1:
                pen += poids_b2b
            elif st.dernier_creneau == slot_index - 2:
                pen += poids_quasi

        # équilibrage intérieur/extérieur
        diff = st.matchs_interieur - st.matchs_exterieur  # >0 trop intérieur
        if type_terrain == "INTERIEUR":
            if diff > 0:
                pen += poids_io * diff
        else:
            if diff < 0:
                pen += poids_io * (-diff)

    return pen


def enregistrer_match(
    equipe_a_id: int,
    equipe_b_id: int,
    slot_index: int,
    type_terrain: str,
    stats_by_team: dict[int, StatsPlanningEquipe],
) -> None:
    """
    Met à jour les stats après placement effectif.
    """
    for tid in (equipe_a_id, equipe_b_id):
        st = stats_by_team.setdefault(tid, StatsPlanningEquipe())
        if st.dernier_creneau is not None:
            if st.dernier_creneau == slot_index - 1:
                st.enchainements_1 += 1
            elif st.dernier_creneau == slot_index - 2:
                st.enchainements_2 += 1

        st.dernier_creneau = slot_index

        if type_terrain == "INTERIEUR":
            st.matchs_interieur += 1
        else:
            st.matchs_exterieur += 1


def calculer_metriques(stats_by_team: dict[int, StatsPlanningEquipe], nb_matchs: int) -> MetriquesPlanning:
    nb_equipes = len(stats_by_team)
    b2b = sum(st.enchainements_1 for st in stats_by_team.values())
    quasi = sum(st.enchainements_2 for st in stats_by_team.values())
    desequilibres = [st.desequilibre_io for st in stats_by_team.values()] or [0]
    return MetriquesPlanning(
        nb_matchs=nb_matchs,
        nb_equipes=nb_equipes,
        nb_back_to_back=b2b,
        nb_quasi_back_to_back=quasi,
        desequilibre_io_total=sum(desequilibres),
        desequilibre_io_max=max(desequilibres),
    )
