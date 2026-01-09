# API_REFERENCE.md

Ce document liste les **endpoints actuels** et les **endpoints prévus** de l’API *Nuit du Basket*.

* Base API (actuelle) : `/api/admin/`
* Public : **non implémenté** (backend uniquement pour le moment)

## Conventions

* Tous les endpoints ci-dessous sont **réservés aux admins** (permission : `IsAdminUser` / `is_staff=True`).
* La logique métier se trouve dans des **services** (pas dans les views).
* Les endpoints marqués **En pause** ne doivent pas être implémentés tant que les règles métier associées ne sont pas figées.

## Statuts

* **Implémenté** : endpoint existant et testé
* **Prévu** : endpoint à venir
* **En pause** : bloqué tant que les règles ne sont pas figées

---

## 1 Éditions

### GET `/api/admin/editions/`

* Rôle : lister les éditions
* Statut : **Implémenté**

### POST `/api/admin/editions/`

* Rôle : créer une édition
* Statut : **Implémenté**

### GET `/api/admin/editions/{id}/`

* Rôle : lire une édition
* Statut : **Implémenté**

### PUT/PATCH `/api/admin/editions/{id}/`

* Rôle : modifier une édition
* Statut : **Implémenté**
* Note (future règle process) : certaines modifications pourront être bloquées quand le tournoi a démarré

### DELETE `/api/admin/editions/{id}/`

* Rôle : supprimer une édition
* Statut : **Implémenté**
* Note (future règle process) : suppression probablement interdite après inscriptions/matchs

---

## 2 Tournois (Rookie / Loisir / Compétiteur)

Les tournois existent **toujours** en 3 codes (pas de création libre).

### GET `/api/admin/tournois/`

* Rôle : lister les tournois (généralement filtrés par édition)
* Statut : **Implémenté**

### GET `/api/admin/tournois/{id}/`

* Rôle : lire un tournoi
* Statut : **Prévu** (optionnel selon besoins)

### PUT/PATCH `/api/admin/tournois/{id}/`

* Rôle : modifier le `libelle` (et potentiellement un futur `est_actif`)
* Statut : **Prévu**

---

## 3 Inscriptions : équipes et joueurs

### Équipes

### GET `/api/admin/equipes/`

* Rôle : lister les équipes (filtres : édition, tournoi, statut…)
* Statut : **Prévu**

### POST `/api/admin/equipes/`

* Rôle : créer une équipe (souvent en BROUILLON)
* Statut : **Prévu**

### GET `/api/admin/equipes/{id}/`

* Rôle : lire une équipe
* Statut : **Prévu**

### PUT/PATCH `/api/admin/equipes/{id}/`

* Rôle : modifier une équipe
* Statut : **Prévu**

### POST `/api/admin/equipes/{id}/valider/`

* Rôle : valider une inscription (contrôles min/max, âge Rookie, etc.)
* Statut : **Prévu**

### DELETE `/api/admin/equipes/{id}/`

* Rôle : supprimer une équipe
* Statut : **Prévu** (avec règles process à définir selon état tournoi)

### Joueurs

### GET `/api/admin/joueurs/`

* Rôle : lister les joueurs (filtres : édition, tournoi, équipe…)
* Statut : **Prévu**

### POST `/api/admin/joueurs/`

* Rôle : ajouter un joueur à une équipe
* Statut : **Prévu**

### PUT/PATCH `/api/admin/joueurs/{id}/`

* Rôle : modifier un joueur
* Statut : **Prévu**

### DELETE `/api/admin/joueurs/{id}/`

* Rôle : supprimer un joueur
* Statut : **Prévu** (avec règles process à définir)

---

## 4 Phases (structure)

### GET `/api/admin/phases-globales/`

* Rôle : lister les phases globales
* Statut : **Prévu**

### POST `/api/admin/phases-globales/`

* Rôle : créer une phase globale (Phase 1 / Phase 2 / Finale)
* Statut : **Prévu**

### POST `/api/admin/phases-globales/{id}/ouvrir/`

* Rôle : passer une phase globale en OUVERTE
* Statut : **Prévu**

### POST `/api/admin/phases-globales/{id}/cloturer/`

* Rôle : clôturer une phase globale (+ toutes ses sous-phases)
* Statut : **En pause**
* Dépendances : règles Phase 2 non figées

### GET `/api/admin/sous-phases/`

* Rôle : lister les sous-phases (par phase globale / tournoi / branche)
* Statut : **Prévu**

---

## 5 Groupes

### GET `/api/admin/groupes/`

* Rôle : lister les groupes (souvent filtrés par sous-phase)
* Statut : **Implémenté**

### GET `/api/admin/groupes/{id}/`

* Rôle : lire un groupe
* Statut : **Prévu** (optionnel)

### POST `/api/admin/groupes/generer/`

* Rôle : générer automatiquement les groupes pour une sous-phase
* Statut : **Implémenté**
* Note : la génération liée à la **Phase 2** est **en pause** tant que les règles de répartition Challenge/Consolante ne sont pas figées

### POST `/api/admin/groupes/swap-equipes/`

* Rôle : interchanger deux équipes entre deux groupes de la même sous-phase
* Statut : **Implémenté**

### DELETE `/api/admin/groupes/{id}/`

* Rôle : supprimer un groupe
* Statut : **Prévu** (process à cadrer)

---

## 6 Matchs

### GET `/api/admin/matchs/`

* Rôle : lister les matchs (filtres : édition, phase, sous-phase, groupe, statut, terrain, créneau…)
* Statut : **Implémenté** (si endpoint déjà créé) / sinon **Prévu**

### POST `/api/admin/matchs/generer/`

* Rôle : générer tous les matchs d’une phase globale (tous tournois confondus)
* Statut : **Implémenté** (si endpoint déjà créé) / sinon **Prévu**

### POST `/api/admin/matchs/{id}/planifier/`

* Rôle : modifier manuellement terrain/créneau d’un match
* Statut : **Prévu**

---

## 7 Planning

### POST `/api/admin/phases-globales/{id}/planning/`

* Rôle : générer le planning (affectation créneau + terrain) pour une phase globale
* Statut : **Implémenté**
* Réponse attendue :

  * `matchs_planifies`
  * `creneaux_utilises`
  * `metriques` (si activé)

### GET `/api/admin/creneaux/`

* Rôle : lister les créneaux d’une édition
* Statut : **Prévu**

### GET `/api/admin/terrains/`

* Rôle : lister les terrains d’une édition
* Statut : **Prévu**

### POST `/api/admin/pauses-planning/`

* Rôle : créer une pause nommée (concours de shoot)
* Statut : **Prévu**

### PUT/PATCH `/api/admin/pauses-planning/{id}/`

* Rôle : modifier / activer / désactiver une pause
* Statut : **Prévu**

---

## 8 Feuilles de match

### POST `/api/admin/matchs/{id}/feuille/`

* Rôle : créer ou récupérer la feuille de match (MatchSheet)
* Statut : **Implémenté**
* Note : endpoint idempotent (si déjà existante, renvoie la feuille)

### GET `/api/admin/matchs/{id}/feuille/`

* Rôle : récupérer les infos de feuille (et futur export PDF)
* Statut : **Prévu**

---

## 9 Scores

### POST `/api/admin/matchs/{id}/score/`

* Rôle : saisir un score (non validé)
* Statut : **Implémenté**

### POST `/api/admin/matchs/{id}/score/valider/`

* Rôle : valider le score (verrouillage + match terminé + recalcul classement)
* Statut : **Implémenté**

### POST `/api/admin/matchs/{id}/forfait/`

* Rôle : déclarer un forfait (FORFAIT_A / FORFAIT_B / DOUBLE_FORFAIT)
* Statut : **Prévu**

---

## 10 Classements

### GET `/api/admin/groupes/{id}/classement/`

* Rôle : obtenir le classement d’un groupe
* Statut : **Prévu**

### PUT/PATCH `/api/admin/classements/{id}/rang-manuel/`

* Rôle : saisir le départage manuel en cas d’égalité ≥3
* Statut : **Prévu**

---

## 11 Phase 2 (Challenge / Consolante)

### POST `/api/admin/phases-globales/{id}/generer-phase2/`

* Rôle : générer la phase 2 depuis la phase 1 (création sous-phases, affectations, groupes)
* Statut : **En pause**
* Raison : règles de répartition (50/50 + cas impairs + décision admin) **non figées**

---

## OpenAPI / Swagger (documentation auto)

Si `drf-spectacular` est activé :

* Schéma OpenAPI (YAML/JSON) : `/api/schema/`
* Swagger UI : `/api/docs/`

---

## Historique

* 2026-01-07 : inventaire initial des endpoints admin (édition, tournois, groupes, planning, feuilles, scores)
* 2026-01-08 : ajout des endpoints prévus (inscriptions, phases, forfaits, classements) et marquage des blocs "en pause" (Phase 2, clôture phase)
