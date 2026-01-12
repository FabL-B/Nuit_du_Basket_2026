# ROADMAP — Nuit du Basket (mise à jour)

## Phase 1 — Fondations techniques ✅

* 1.1 Initialisation projet Django / DRF ✅
* 1.2 Architecture modulaire (apps métier) ✅
* 1.3 Modèles de base (Edition, Tournoi, Equipe) ✅
* 1.4 Contraintes DB & validations métier de base ✅

---

## Phase 2 — Groupes & Inscriptions ✅

* 2.1 Règles de tailles de groupes Phase 1 (min 8, 4/5 uniquement) ✅
* 2.2 Validation équipes par tournoi (bornes min/max) ✅
* 2.3 Contrôle d’âge Rookie (≥ 15 ans) ✅
* 2.4 Génération automatique des groupes Phase 1 (v2) ✅
* 2.5 Swap manuel d’équipes entre groupes (même sous-phase) ✅

> ℹ️ **Note** : l’interdiction des groupes de 3 est désormais **explicitement limitée à la Phase 1**.

---

## Phase 3 — Matchs, Classements & Planning ✅

* 3.1 Génération des matchs par phase globale (round-robin groupe) ✅
* 3.2 Modèle Match / Score / Feuille de match ✅
* 3.3 Validation score verrouillante + recalcul classement auto ✅
* 3.4 Classement (points, diff, égalités) + recalcul sécurisé ✅
* 3.5 Génération planning phase globale (créneaux + terrains) ✅
* 3.6 Contraintes strictes planning (collisions, doublons, simultanéité) ✅
* 3.7 Heuristiques planning (enchaînements, indoor/outdoor, repos) ✅
* 3.8 Pauses nommées planning + recalcul créneaux ✅

---

## Phase 4 — Transitions & Phases avancées ✅

### 4.1 Clôture Phase 1 ✅

* Tous les matchs doivent être finalisés
* Classements recalculés et cohérents
* Égalités ≥ 3 équipes :

  * **rang_manuel obligatoire**
  * clôture refusée tant que non renseigné

---

### 4.2 Passage Phase 1 → Phase 2 ✅ (règles figées, implémentation en pause)

* Phase 2 composée de deux branches :

  * Challenge
  * Consolante
* Classement Phase 1 utilisé comme référence
* Cas pair :

  * répartition automatique 50 % / 50 %
* Cas impair :

  * **décision admin obligatoire**
  * choix explicite de l’équipe surnuméraire (Challenge ou Consolante)

---

### 4.3 Groupes Phase 2 ✅ (règles clarifiées)

* **Groupes de 3 équipes autorisés**
* Groupes de 4 ou 5 toujours autorisés
* Une branche peut contenir :

  * un seul groupe
  * ou plusieurs groupes
* Aucun minimum strict d’équipes requis

> ⚠️ Implémentation volontairement en pause tant que :
>
> * les tests Phase 2 ne sont pas écrits
> * l’API admin associée n’est pas définie

---

### 4.4 Génération matchs Phase 2 ✅

* Round-robin intra-groupe
* Règles identiques à Phase 1

---

### 4.5 Phase Finale ✅

* Règles non définies
* Hors scope actuel

---

## Phase 5 — API Admin & Sécurité ✅

* 5.1 Permissions admin globales (is_staff) ✅
* 5.2 Endpoints admin CRUD (Editions, Tournois, Phases, Groupes, Matchs) ✅
* 5.3 Actions admin métier :

  * swap équipes
  * génération planning
  * génération feuilles de match
  * forfaits
* 5.4 Documentation OpenAPI (drf-spectacular) 🟨

---

## Phase 6 — Qualité & Documentation 🟨

* 6.1 Tests unitaires & intégration (pytest) 🟨
* 6.2 RULES_ENGINE.md (règles métier figées) 🟨
* 6.3 DATA_MODEL.md (modèle exhaustif) 🟨
* 6.4 API_REFERENCE.md (endpoints actuels + à venir) 🟨
* 6.5 AI_GUIDE.md / CONTRIBUTING.md 🟨

---

## Historique

### 2026-01-07

* Groupes Phase 1 (min 8, 4/5 uniquement)
* Validation équipes + âge Rookie
* Génération matchs, scores, classements
* Planning global + heuristiques
* Pauses nommées planning

### 2026-01-08

* Clarification officielle Phase 2 :

  * groupes de 3 autorisés
  * décision admin requise en cas impair
* Blocage volontaire implémentation Phase 2
* API admin en cours (DRF + OpenAPI)

---

### Légende

* ✅ Terminé
* 🟨 Règles figées / implémentation partielle
* ⬜ À faire
