# 📄 `ROADMAP.md`

Ce document décrit **l’état d’avancement**, **les blocs fonctionnels**, et **l’ordre de développement** de l’API Nuit du Basket.

Il est **mis à jour à chaque bloc validé**.

---

## 1. Légende des statuts

* ⬜ À faire
* 🟨 En cours
* ✅ Validé
* ⛔ Bloqué (règle à clarifier)
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
| 0.6  | ROADMAP.md                         | 🟨     |

---

## 3. Phase 1 — Inscriptions & structure tournoi

### 3.1 Éditions

| Bloc | Description              | Statut |
| ---- | ------------------------ | ------ |
| 1.1  | Modèle Edition           | ✅      |
| 1.2  | API CRUD Edition (admin) | ⬜      |

### 3.2 Tournois

| Bloc | Description                                              | Statut |
| ---- | -------------------------------------------------------- | ------ |
| 1.3  | Modèle Tournoi (Rookie/Loisir/Compétiteur)               | ✅      |
| 1.4  | Création auto des 3 tournois à la création d’une édition | ⬜      |

### 3.3 Inscriptions

| Bloc | Description                       | Statut |
| ---- | --------------------------------- | ------ |
| 1.5  | Modèles Équipe / Joueur           | ✅      |
| 1.6  | Validation d’équipe (4–5 joueurs) | ✅      |
| 1.7  | API CRUD Équipe (brouillon)       | ⬜      |
| 1.8  | API CRUD Joueur                   | ⬜      |

---

## 4. Phase 2 — Phases & groupes

### 4.1 Phases

| Bloc | Description                            | Statut |
| ---- | -------------------------------------- | ------ |
| 2.1  | Modèles PhaseGlobale / SousPhase       | ✅      |
| 2.2  | Génération automatique des sous-phases | ⬜      |
| 2.3  | Clôture PhaseGlobale                   | ⬜      |

### 4.2 Groupes

| Bloc | Description                          | Statut |
| ---- | ------------------------------------ | ------ |
| 2.4  | Modèles Groupe / GroupeEquipe        | ✅      |
| 2.5  | Génération automatique des groupes   | ⬜      |
| 2.6  | Ajustement manuel des groupes (swap) | ⬜      |

---

## 5. Phase 3 — Matchs & planning

### 5.1 Matchs

| Bloc | Description                               | Statut |
| ---- | ----------------------------------------- | ------ |
| 3.1  | Modèle Match                              | ⬜      |
| 3.2  | Génération des matchs (par phase globale) | ⬜      |
| 3.3  | Modèle MatchSheet                         | ⬜      |
| 3.4  | Modèle Score                              | ⬜      |

### 5.2 Planning

| Bloc | Description                               | Statut |
| ---- | ----------------------------------------- | ------ |
| 3.5  | Modèles Terrain / Créneau                 | ⬜      |
| 3.6  | Génération planning (créneaux + terrains) | ⬜      |
| 3.7  | Ajustement manuel planning                | ⬜      |

---

## 6. Phase 4 — Classements & transitions

| Bloc | Description                      | Statut |
| ---- | -------------------------------- | ------ |
| 4.1  | Modèle Classement                | ⬜      |
| 4.2  | Calcul classement automatique    | ⬜      |
| 4.3  | Tie-breaks (diff / points / H2H) | ⬜      |
| 4.4  | Passage Phase 1 → Phase 2        | ⬜      |
| 4.5  | Phase finale (brackets manuels)  | ⬜      |

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
| 6.3  | README final                 | ⬜      |

---

## 9. Règles d’évolution de la roadmap

* Un bloc passe à **✅** uniquement quand :

  * le code est écrit
  * les tests passent
  * la règle est documentée
* Toute modification fonctionnelle implique :

  * mise à jour de `RULES_ENGINE.md`
  * mise à jour de `DATA_MODEL.md` si nécessaire
  * mise à jour de cette roadmap
