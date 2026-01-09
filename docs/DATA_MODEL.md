# 📄 DATA_MODEL.md (mise à jour)

Ce document décrit le **modèle de données** actuel de l’API Nuit du Basket (backend Django/DRF), ainsi que les **évolutions prévues** déjà décidées côté règles métier.

Objectifs :
- Décrire les modèles (champs + relations) de façon lisible
- Expliquer les invariants (contraintes DB) vs règles métier (validation/service)
- Clarifier **Phase 1 vs Phase 2** (notamment sur les tailles de groupes)

---

## 1. Principes généraux

### 1.1 Terminologie
- **Édition** : l’évènement annuel (ex: “NDB 2026”)
- **Tournoi** : une catégorie fixe par édition : Rookie / Loisir / Compétiteur
- **Phase globale** : Phase 1, Phase 2, Finale (niveau “édition”)
- **Sous-phase** : déclinaison d’une phase globale **par tournoi** et par branche (aucune/challenge/consolante)
- **Groupe** : groupe d’équipes dans une sous-phase
- **Match** : opposition entre 2 équipes (créé avant planification)
- **Planning** : affectation des matchs à un créneau + terrain
- **Score** : résultat saisi puis validé (déclenche le recalcul de classement)
- **Classement** : stats calculées par groupe

### 1.2 Contraintes : DB vs métier
- Les **contraintes DB** empêchent les incohérences irréparables (unicités, FK, check).
- Les **règles métier** (bornes, âge, génération, process) sont gérées par :
  - validations `clean()` / `full_clean()` quand c’est pertinent
  - services (transactions atomiques) pour la logique de génération / process.

---

## 2. Core — Édition

### 2.1 `core.Edition`

Une édition représente une année/évènement.

Champs :
- `nom` (CharField, unique)
- `date_evenement` (DateField, unique)
- `heure_debut` (TimeField, default 14:00, modifiable)
- `duree_creneau_minutes` (PositiveSmallIntegerField, default 15)
- `cree_le` / `modifie_le`

Notes :
- `heure_debut` a bien un défaut (choix validé).
- `duree_creneau_minutes` sert à générer des créneaux automatiques.

---

## 3. Tournois

### 3.1 `tournois.Tournoi`

Un tournoi est une **catégorie** au sein d’une édition.
Il y a **toujours** 3 tournois par édition : Rookie / Loisir / Compétiteur.

Champs :
- `edition` (FK Edition, PROTECT, `related_name="tournois"`)
- `code` (CharField choices `CodeTournoi`: ROOKIE/LOISIR/COMPETITEUR)
- `libelle` (CharField, blank=True)

Contraintes DB :
- unique (`edition`, `code`)

---

## 4. Phases (Phase 1 / Phase 2 / Finale)

### 4.1 `phases.PhaseGlobale`

Représente une phase au niveau de l’édition.

Champs :
- `edition` (FK Edition, PROTECT, `related_name="phases_globales"`)
- `type_phase` (choices `TypePhaseGlobale`: PHASE_1 / PHASE_2 / FINALE)
- `sequence` (PositiveSmallIntegerField, default 1)
- `statut` (choices `StatutPhase`: BROUILLON / OUVERTE / CLOTUREE)
- `cree_le` / `modifie_le`

Contraintes DB :
- unique (`edition`, `type_phase`, `sequence`)

### 4.2 `phases.SousPhase`

Une sous-phase est la déclinaison d’une phase globale :
- **par tournoi** (Rookie/Loisir/Compétiteur)
- et éventuellement par **branche** (Challenge/Consolante)

Champs :
- `phase_globale` (FK PhaseGlobale, PROTECT, `related_name="sous_phases"`)
- `tournoi` (FK Tournoi, PROTECT, `related_name="sous_phases"`)
- `branche` (choices `BrancheSousPhase`: AUCUNE / CHALLENGE / CONSOLANTE)
- `statut` (BROUILLON / OUVERTE / CLOTUREE)
- `cree_le` / `modifie_le`

Contraintes DB :
- unique (`phase_globale`, `tournoi`, `branche`)

### 4.3 Clarification Phase 1 vs Phase 2 (impact data)

Phase 1 :
- Une seule branche : `AUCUNE`
- Groupes générés selon les règles strictes Phase 1 (voir section Groupes)

Phase 2 :
- Deux branches par tournoi : `CHALLENGE` et `CONSOLANTE`
- Les équipes sont réparties depuis Phase 1, avec règles process (décision admin si impair)
- **Les groupes de 3 équipes sont autorisés en Phase 2** (clarification officielle)

> Note : le modèle actuel supporte Phase 2 via `SousPhase.branche`.

### 4.4 Évolution prévue (process Phase 2, à implémenter plus tard)

Pour tracer la décision admin en cas de répartition impaire (par tournoi) :
- Nouveau modèle envisagé : `phases.DecisionRepartitionPhase2`

Champs proposés :
- `phase1` (FK PhaseGlobale de type PHASE_1, PROTECT)
- `tournoi` (FK Tournoi, PROTECT)
- `equipe` (FK Equipe, PROTECT) — équipe surnuméraire
- `destination` (choices : CHALLENGE / CONSOLANTE)
- `decidee_par` (FK user, PROTECT)
- `decidee_le` (DateTime)

Contraintes proposées :
- unique (`phase1`, `tournoi`) (une décision max par tournoi et par Phase 1)

---

## 5. Groupes

### 5.1 `groupes.Groupe`

Champs :
- `sous_phase` (FK SousPhase, PROTECT, `related_name="groupes"`)
- `code` (CharField, ex: "A", "B"...)
- `cree_le` / `modifie_le`

Contraintes DB :
- unique (`sous_phase`, `code`)

### 5.2 `groupes.GroupeEquipe`

Table d’affectation équipe → groupe.

Champs :
- `groupe` (FK Groupe, CASCADE, `related_name="equipes"`)
- `equipe` (FK Equipe, PROTECT, `related_name="groupes"`)
- `seed` (PositiveSmallIntegerField, null=True, blank=True)
- `cree_le`

Contraintes DB :
- unique (`groupe`, `equipe`)
- unique (`groupe`, `seed`) si `seed` non null (constraint conditionnelle)

Validation métier (modèle) :
- `equipe.edition_id == groupe.sous_phase.phase_globale.edition_id`
- `equipe.tournoi_id == groupe.sous_phase.tournoi_id`

### 5.3 Règles de taille de groupe (rappel — pas du DB)

Phase 1 (strict) :
- minimum 8 équipes pour démarrer un tournoi
- **groupes de 3 interdits**
- tailles autorisées : 4 et 5 uniquement (avec règles 8/9/10/11/≥12)

Phase 2 (plus souple) :
- **groupes de 3 autorisés**
- tailles possibles : 3, 4, 5
- une branche (challenge/consolante) peut avoir **un seul groupe** si effectif réduit

> Ces règles sont portées par les services de génération, pas par des contraintes DB.

---

## 6. Inscriptions

### 6.1 `inscriptions.Equipe`

Champs :
- `edition` (FK Edition, PROTECT, `related_name="equipes"`)
- `tournoi` (FK Tournoi, PROTECT, `related_name="equipes"`)
- `nom` (CharField)
- `club_nom` (CharField, blank=True) (selon implémentation)
- `statut` (choices `StatutEquipe`: BROUILLON / VALIDEE / REFUSEE, selon implémentation)
- `cree_le` / `modifie_le`

Contraintes DB (rappel des décisions) :
- Unicité du nom d’équipe : **à l’échelle de l’édition** (décision validée précédemment)
  - ex: unique (`edition`, `nom`)

Règles métier (service) :
- Bornes de joueurs selon tournoi :
  - Loisir : 3 à 5
  - Rookie : 3 à 4
  - Compétiteur : 3 à 4
- Rookie : âge ≥ 15 ans à `Edition.date_evenement` (à la validation)

### 6.2 `inscriptions.Joueur`

Champs :
- `equipe` (FK Equipe, CASCADE/PROTECT selon choix, `related_name="joueurs"`)
- `prenom` / `nom`
- `date_naissance` (null=True, blank=True)
- `email` (blank=True)
- `telephone` (blank=True)
- `cree_le` / `modifie_le`

---

## 7. Matchs, feuilles, scores

### 7.1 `matchs.Match`

Champs :
- `edition` (FK Edition, PROTECT)
- `phase_globale` (FK PhaseGlobale, PROTECT)
- `sous_phase` (FK SousPhase, PROTECT)
- `groupe` (FK Groupe, PROTECT)
- `equipe_a` (FK Equipe, PROTECT)
- `equipe_b` (FK Equipe, PROTECT)
- `creneau` (FK planning.Creneau, SET_NULL, null=True, blank=True)
- `terrain` (FK planning.Terrain, SET_NULL, null=True, blank=True)
- `statut` (choices StatutMatch : A_PLANIFIER / PLANIFIE / TERMINE / FORFAIT_A / FORFAIT_B / DOUBLE_FORFAIT)
- `cree_le` / `modifie_le`

Contraintes DB :
- check : `equipe_a != equipe_b`
- unique (`groupe`, `equipe_a`, `equipe_b`) (ordre strict)
  - la déduplication “non ordonnée” est gérée au niveau génération/service

Validation métier (modèle) :
- cohérence édition/phase/sous-phase/groupe
- cohérence tournoi des équipes avec la sous-phase

### 7.2 `matchs.MatchSheet`

Champs :
- `match` (OneToOne Match, CASCADE)
- `sheet_code` (uuid string, unique, non éditable)
- `cree_le`

Note :
- la feuille est un identifiant imprimable + support d’export.
- des champs additionnels pourront être ajoutés plus tard si on veut “capturer” la feuille (fautes, chasubles, etc).

### 7.3 `matchs.Score`

Champs :
- `match` (OneToOne Match, CASCADE)
- `points_a` / `points_b`
- `valide_le` (nullable)
- `valide_par` (FK user, nullable)
- `cree_le` / `modifie_le`

Règles métier :
- Score validé = verrouillé (modification interdite)
- Validation déclenche recalcul classement (service)

---

## 8. Classements

### 8.1 `classements.Classement`

Champs :
- `groupe` (FK Groupe, CASCADE/PROTECT selon implémentation)
- `equipe` (FK Equipe, PROTECT)
- `joues`, `gagnes`, `perdus`, `egalites`
- `points_marques`, `points_encaisses`, `difference`
- `points_classement`
- `rang_manuel` (nullable) — utilisé pour les égalités ≥ 3 (process)
- `note_admin` (nullable, optionnel)
- `maj_le`

Contraintes DB :
- unique (`groupe`, `equipe`)

Process :
- recalcul complet à partir des matchs finalisés du groupe
- si égalité ≥ 3 : `rang_manuel` requis pour clôturer la phase

---

## 9. Planning

### 9.1 `planning.Terrain`

Champs :
- `edition` (FK Edition, PROTECT)
- `nom` (CharField)
- `type_terrain` (choices TypeTerrain : INTERIEUR / EXTERIEUR)
- `ordre` (int)
- `est_actif` (bool, default True)
- `cree_le` / `modifie_le`

### 9.2 `planning.Creneau`

Champs :
- `edition` (FK Edition, PROTECT)
- `index` (int)
- `debut` (DateTime)
- `duree_minutes` (default = Edition.duree_creneau_minutes)
- `cree_le`

Notes :
- Les créneaux peuvent être créés automatiquement au moment de planifier.
- Les pauses nommées impactent la séquence temporelle (décalage de reprise).

### 9.3 Évolution prévue : pauses nommées (planning)

Pour supporter “concours de shoot” et autres pauses :
- Modèle envisagé : `planning.PausePlanning`

Champs proposés :
- `edition` (FK Edition, PROTECT)
- `nom` (CharField) — ex : “Concours de shoot”
- `debut` (DateTime)
- `duree_minutes` (PositiveSmallInteger)
- `cree_le`

Effet :
- lors de la génération planning, les matchs prévus pendant la pause sont décalés après.

---
