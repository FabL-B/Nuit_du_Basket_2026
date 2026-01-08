# 📄 `ROADMAP.md` (mise à jour)

Cette roadmap reflète **l’état réel et contractuel** du projet après l’ajout des **nouvelles règles métier**.
Elle est alignée avec :

* `RULES_ENGINE.md`
* `DATA_MODEL.md`

---

## 1. Légende des statuts

* ⬜ À faire
* 🟨 En cours
* ✅ Validé
* ⛔ Bloqué (règles modifiées / à intégrer)
* 🔁 À revoir

---

## 2. Phase 0 — Fondations du projet

| Bloc | Description                        | Statut |
| ---- | ---------------------------------- | ------ |
| 0.1  | Initialisation repo + Django + DRF | ✅      |
| 0.2  | AI_GUIDE.md                        | ✅      |
| 0.3  | ARCHITECTURE.md                    | ✅      |
| 0.4  | DATA_MODEL.md                      | ✅      |
| 0.5  | RULES_ENGINE.md                    | ✅      |
| 0.6  | ROADMAP.md                         | ✅      |
| 0.7  | README.md                          | ✅      |

---

## 3. Phase 1 — Inscriptions & structure tournoi

### 3.1 Éditions

| Bloc | Description                                                     | Statut |
| ---- | --------------------------------------------------------------- | ------ |
| 1.1  | Modèle Edition                                                  | ✅      |
| 1.2  | API CRUD Edition (admin)                                        | ⬜      |
| 1.3  | Création automatique des 3 tournois à la création d’une édition | ⬜      |

---

### 3.2 Tournois

| Bloc | Description                                    | Statut |
| ---- | ---------------------------------------------- | ------ |
| 1.4  | Modèle Tournoi (Rookie / Loisir / Compétiteur) | ✅      |
| 1.5  | Garde-fou : exactement 3 tournois par édition  | ⬜      |

---

### 3.3 Inscriptions

| Bloc | Description                                                  | Statut |
| ---- | ------------------------------------------------------------ | ------ |
| 1.6  | Modèles Équipe / Joueur                                      | ✅      |
| 1.7  | Validation équipe (min/max joueurs par tournoi)              | ✅      |
| 1.8  | Contrôle d’âge Rookie (≥ 15 ans)                             | ✅      |
| 1.9  | Refus inscription si seuil tournoi invalide (ex: 11 équipes) | ✅      |
| 1.10 | API CRUD Équipe (brouillon)                                  | ⬜      |
| 1.11 | API CRUD Joueur                                              | ⬜      |

---

## 4. Phase 2 — Phases & groupes

### 4.1 Phases

| Bloc | Description                            | Statut |
| ---- | -------------------------------------- | ------ |
| 2.1  | Modèles PhaseGlobale / SousPhase       | ✅      |
| 2.2  | Génération automatique des sous-phases | ✅      |
| 2.3  | Clôture PhaseGlobale (+ sous-phases)   | ✅      |

---

### 4.2 Groupes

| Bloc | Description                                             | Statut |
| ---- | ------------------------------------------------------- | ------- |
| 2.4  | Modèles Groupe / GroupeEquipe                           | ✅      |
| 2.5  | Génération automatique des groupes (anciennes règles)   | ⛔      |
| 2.5b | Génération groupes (min 8, pas de 3, cas 9/10/11/12+)   | ✅      |
| 2.6  | Ajustement manuel des groupes (swap contrôlé)           | ✅      |

---

## 5. Phase 3 — Matchs & planning

### 5.1 Matchs

| Bloc | Description                               | Statut |
| ---- | ----------------------------------------- | ------ |
| 3.1  | Modèle Match                              | ✅      |
| 3.2  | Génération des matchs (par phase globale) | ✅      |
| 3.3  | Modèle MatchSheet                         | ✅      |
| 3.4  | Modèle Score                              | ✅      |

---

### 5.2 Planning

| Bloc | Description                                                | Statut |
| ---- | ---------------------------------------------------------- | ------ |
| 3.5  | Modèles Terrain / Créneau                                  | ✅      |
| 3.6  | Génération planning (créneaux + terrains)                  | ✅      |
| 3.7  | Règles souples (indoor/outdoor, éviter matchs consécutifs) | ✅      |
| 3.8  | Pauses nommées dans le planning (concours, événements)     | ✅      |
| 3.9  | Ajustement manuel du planning                              | ⬜      |

---

## 6. Phase 4 — Classements & transitions

| Bloc | Description                                        | Statut |
| ---- | -------------------------------------------------- | ------ |
| 4.1  | Modèle Classement                                  | ✅      |
| 4.2  | Calcul automatique du classement                   | ✅      |
| 4.3  | Tie-breaks (diff / points / confrontation directe) | ✅      |
| 4.4  | Passage Phase 1 → Phase 2                          | ⬜      |
| 4.5  | Phases finales (brackets manuels assistés)         | ⬜      |

---

## 7. Phase 5 — API & sécurité

| Bloc | Description                       | Statut |
| ---- | --------------------------------- | ------ |
| 5.1  | Permissions admin globales        | ⬜      |
| 5.2  | Endpoints DRF structurés          | ⬜      |
| 5.3  | Validation des transitions d’état | ⬜      |

---

## 8. Phase 6 — Qualité & livrables

| Bloc | Description                  | Statut |
| ---- | ---------------------------- | ------ |
| 6.1  | Tests complets règles métier | ⬜      |
| 6.2  | Documentation API            | ⬜      |
| 6.3  | Revue finale README          | ⬜      |

---

## 9. Règles d’évolution de la roadmap

* Un bloc passe à **✅** uniquement si :

  * le code est implémenté
  * les tests passent
  * la documentation est à jour
* Un bloc passe à **⛔** dès qu’une règle métier change.
* Toute nouvelle règle implique :

  * `RULES_ENGINE.md`
  * `DATA_MODEL.md` (si impact structurel)
  * cette roadmap

---

## Historique

* 2026-01-07 :
  Bloc 2.5 suspendu et remplacé par 2.5b suite aux nouvelles règles de groupes (min 8 équipes, pas de groupes de 3, cas 9/10/11/12+), ajout des règles d’âge Rookie, tailles d’équipes par tournoi, et pauses nommées dans le planning.
