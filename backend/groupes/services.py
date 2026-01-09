from .services_shared import ErreurGenerationGroupes, _creer_groupes_et_affectations
from .services_phase1 import (
    _calculer_tailles_groupes_phase1 as _calculer_tailles_groupes_v2,
    generer_groupes_phase1_pour_sous_phase as generer_groupes_pour_sous_phase,
)
from .services_phase2 import (
    _calculer_tailles_groupes_phase2,
    generer_groupes_phase2_pour_sous_phase_avec_equipes,
)
