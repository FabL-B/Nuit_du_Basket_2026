# 📄 `DATA_MODEL.md`

Ce document décrit le **modèle de données** de l’API Nuit du Basket :

* entités
* champs
* relations
* contraintes
* statuts

Il sert de référence pour :

* les migrations
* les règles métier
* la génération (groupes, matchs, planning)
* la documentation API

---

## 1. Conventions générales

### Langue

* Champs et libellés : français
* Codes internes : valeurs stables (ex: `ROOKIE`, `PHASE_1`, etc.)

### Dates / heures

* `Edition.date_evenement` = date du tournoi
* `Edition.heure_debut` = 14:00 par défaut (modifiable)
* `Creneau.start_at` = datetime (date + heure)

### Suppression

* Préférence pour statuts plutôt que suppression.
* Certaines FK sont en `PROTECT` pour éviter les incohérences.

---

## 2. Diagramme conceptuel (vue simple)

* **Edition**

  * 3 × **Tournoi**
  * n × **Equipe**
  * n × **PhaseGlobale**
  * n × **Terrain**
  * n × **Creneau**
* **PhaseGlobale**

  * n × **SousPhase**
  * n × **Match**
* **SousPhase**

  * n × **Groupe**
* **Groupe**

  * n × **GroupeEquipe**
  * n × **Match**
* **Equipe**

  * 4–5 × **Joueur**
* **Match**

  * 1 × **MatchSheet**
  * 1 × **Score**
  * 0..1 × **Terrain**
  * 0..1 × **Creneau**

---

## 3. Modèles

## 3.1 `core.Edition`

### Rôle

Représente une édition annuelle (ex: “NDB 2026”).

### Champs

* `nom` (CharField, unique)
* `date_evenement` (DateField, unique)
* `heure_debut` (TimeField, default 14:00)
* `duree_creneau_minutes` (PositiveSmallIntegerField, default 15)
* `cree_le` (DateTimeField, auto_now_add)
* `modifie_le` (DateTimeField, auto_now)

### Contraintes

* `nom` unique
* `date_evenement` unique

---

## 3.2 `tournois.Tournoi`

### Rôle

Sous-tournoi d’une édition : Rookie / Loisir / Compétiteur.

### Champs

* `edition` (FK → Edition, PROTECT)
* `code` (CharField, choices: `ROOKIE`, `LOISIR`, `COMPETITEUR`)
* `libelle` (CharField, blank)

### Contraintes

* UniqueConstraint(`edition`, `code`)
  → 1 seul Rookie/Loisir/Compétiteur par édition.

### Règle métier associée

* Une édition doit contenir **exactement 3 tournois** (contrôlé via service à la création).

---

## 3.3 `phases.PhaseGlobale`

### Rôle

Phase principale planifiée et gérée globalement :

* Phase 1
* Phase 2
* Finale

### Champs

* `edition` (FK → Edition, PROTECT)
* `type_phase` (choices: `PHASE_1`, `PHASE_2`, `FINALE`)
* `sequence` (PositiveSmallIntegerField, default 1)
* `statut` (choices: `BROUILLON`, `OUVERTE`, `CLOTUREE`, default BROUILLON)
* `cree_le`, `modifie_le`

### Contraintes

* UniqueConstraint(`edition`, `type_phase`, `sequence`)

### Règle métier associée

* La clôture d’une phase globale entraîne la clôture de toutes ses sous-phases.

---

## 3.4 `phases.SousPhase`

### Rôle

Déclinaison d’une phase globale par tournoi et branche (challenge/consolante).

### Champs

* `phase_globale` (FK → PhaseGlobale, PROTECT)
* `tournoi` (FK → Tournoi, PROTECT)
* `branche` (choices: `AUCUNE`, `CHALLENGE`, `CONSOLANTE`, default AUCUNE)
* `statut` (choices: `BROUILLON`, `OUVERTE`, `CLOTUREE`, default BROUILLON)
* `cree_le`, `modifie_le`

### Contraintes

* UniqueConstraint(`phase_globale`, `tournoi`, `branche`)

### Règles métier associées

* En Phase 1 : branche = `AUCUNE`
* En Phase 2 : branche = `CHALLENGE` ou `CONSOLANTE`
* En Finale : branche = `CHALLENGE` ou `CONSOLANTE`

---

## 3.5 `inscriptions.Equipe`

### Rôle

Équipe inscrite sur une édition et un tournoi.

### Champs

* `edition` (FK → Edition, PROTECT)
* `tournoi` (FK → Tournoi, PROTECT)
* `nom` (CharField)
* `nom_club` (CharField, blank)
* `statut` (choices: `BROUILLON`, `VALIDEE`, `ARCHIVEE`, default BROUILLON)
* `cree_le`, `modifie_le`

### Contraintes

* UniqueConstraint(`edition`, `nom`)
  → nom unique par édition tous tournois confondus.

### Validations

* Le tournoi choisi doit appartenir à la même édition que l’équipe.

### Règles métier associées

* Une équipe validée doit avoir **4 à 5 joueurs** (contrôlé par service, pas en contrainte DB).

---

## 3.6 `inscriptions.Joueur`

### Rôle

Joueur inscrit dans une équipe.

### Champs

* `equipe` (FK → Equipe, CASCADE)
* `prenom` (CharField)
* `nom` (CharField)
* `date_naissance` (DateField, nullable)
* `email` (EmailField, blank)
* `telephone` (CharField, blank)
* `cree_le`, `modifie_le`

### Contraintes

* Pas de contrainte d’unicité imposée pour l’instant.

---

## 3.7 `groupes.Groupe`

### Rôle

Groupe (poule) d’une sous-phase.

### Champs

* `sous_phase` (FK → SousPhase, PROTECT)
* `code` (CharField, ex: A/B/C…)
* `cree_le`, `modifie_le`

### Contraintes

* UniqueConstraint(`sous_phase`, `code`)

---

## 3.8 `groupes.GroupeEquipe`

### Rôle

Association équipe ↔ groupe.

### Champs

* `groupe` (FK → Groupe, CASCADE)
* `equipe` (FK → Equipe, PROTECT)
* `seed` (PositiveSmallIntegerField, nullable)
* `cree_le`

### Contraintes

* UniqueConstraint(`groupe`, `equipe`)
* UniqueConstraint(`groupe`, `seed`) si `seed` non null

### Validations strictes

* `equipe.edition` doit correspondre à `groupe.sous_phase.phase_globale.edition`
* `equipe.tournoi` doit correspondre à `groupe.sous_phase.tournoi`

---

## 3.9 `planning.Terrain` (à venir)

### Champs prévus

* `edition` (FK → Edition, PROTECT)
* `nom`
* `type_terrain` (choices: `INTERIEUR`, `EXTERIEUR`)
* `ordre` (int)
* `est_actif` (bool)
* `cree_le`, `modifie_le`

---

## 3.10 `planning.Creneau` (à venir)

### Champs prévus

* `edition` (FK → Edition, PROTECT)
* `index` (int)
* `start_at` (datetime)
* `duree_minutes` (default 15)
* `cree_le`

---

## 3.11 `matchs.Match` (à venir)

### Champs prévus

* `edition` (FK → Edition, PROTECT)
* `phase_globale` (FK → PhaseGlobale, PROTECT)
* `sous_phase` (FK → SousPhase, PROTECT)
* `groupe` (FK → Groupe, PROTECT)
* `equipe_a` (FK → Equipe, PROTECT)
* `equipe_b` (FK → Equipe, PROTECT)
* `creneau` (FK → Creneau, nullable)
* `terrain` (FK → Terrain, nullable)
* `statut` (ex: `A_PLANIFIER`, `PLANIFIE`, `TERMINE`, `FORFAIT_A`, etc.)
* `cree_le`, `modifie_le`

### Contraintes prévues

* `equipe_a != equipe_b`
* cohérence édition/tournoi avec la sous-phase
* planification nullable au départ

---

## 3.12 `matchs.Score` (à venir)

### Champs prévus

* `match` (OneToOne → Match)
* `points_a` (int)
* `points_b` (int)
* `valide_le` (datetime nullable)
* `valide_par` (FK User)
* `cree_le`, `modifie_le`

### Règle métier associée

* Le classement est recalculé uniquement quand `valide_le` est renseigné.

---

## 3.13 `matchs.MatchSheet` (à venir)

### Champs prévus

* `match` (OneToOne → Match)
* `sheet_code` (uuid str unique)
* `couleur_chasuble_a` (str)
* `couleur_chasuble_b` (str)
* `fautes_a` (int)
* `fautes_b` (int)
* `equipe_gagnante` (FK Equipe nullable)
* `cree_le`

### Note

* Le numéro de match, créneau, terrain, tournoi, branche etc. sont dérivables depuis `match`.
* La feuille stocke uniquement ce qui est **spécifique à la feuille** (chasubles, fautes, gagnant, etc.).

---

## 3.14 `classements.Classement` (à venir)

### Champs prévus

* `groupe` (FK → Groupe, PROTECT)
* `equipe` (FK → Equipe, PROTECT)
* `joues`, `gagnes`, `perdus`, `egalites`
* `points_pour`, `points_contre`, `diff`
* `points_classement` (win=3, draw=2, loss=1, forfait=0)
* `modifie_le`

### Contraintes prévues

* UniqueConstraint(`groupe`, `equipe`)

### Tie-break (déjà défini)

1. Différence de points (diff)
2. Points marqués
3. Confrontation directe
4. Décision manuelle admin

---

## 4. Statuts et transitions (résumé)

### Équipe

* BROUILLON → VALIDEE (si 4–5 joueurs)
* VALIDEE → ARCHIVEE (plus tard si besoin)

### PhaseGlobale / SousPhase

* BROUILLON → OUVERTE → CLOTUREE

### Match

* A_PLANIFIER → PLANIFIE → TERMINE
* ou FORFAIT_A / FORFAIT_B / DOUBLE_FORFAIT

---

## 5. Validation

Ce document reflète l’état actuel des décisions.
