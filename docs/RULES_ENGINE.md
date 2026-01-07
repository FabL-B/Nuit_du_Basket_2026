# 📄 `RULES_ENGINE.md`

Ce document formalise le **moteur de règles métier** de Nuit du Basket.
Il ne décrit pas le code, mais :

* les invariants à respecter
* les règles de calcul
* les règles de génération
* les validations et transitions d’état
* les points volontairement laissés “extensibles”

Ce document sert de base aux **services** et aux **tests unitaires**.

---

## 1. Définitions rapides

### Edition

Évènement annuel (ex : NDB 2026) contenant tout le tournoi.

### Tournoi

Catégorie fixe : Rookie / Loisir / Compétiteur.

### Phase globale

Niveau de gestion “macro” : Phase 1 / Phase 2 / Finale.
La planification et la génération sont réalisées **au niveau phase globale**.

### Sous-phase

Découpage d’une phase globale par :

* tournoi
* branche (`AUCUNE`, `CHALLENGE`, `CONSOLANTE`)

### Groupe

Poule d’une sous-phase (3 à 5 équipes).

---

## 2. Invariants (règles impossibles à violer)

### 2.1. Tournois

* Une édition contient toujours exactement **3 tournois** :

  * ROOKIE, LOISIR, COMPETITEUR
* Aucun autre code de tournoi n’est autorisé.

### 2.2. Inscription des équipes

* Une équipe appartient à **une seule édition**.
* Une équipe appartient à **un seul tournoi**.
* Le nom d’équipe est **unique dans l’édition** (tous tournois confondus).

### 2.3. Joueurs

* Un joueur appartient à **une seule équipe**.
* Une équipe validée contient **4 à 5 joueurs**.

### 2.4. Groupes

* Un groupe appartient à une **sous-phase**.
* Une équipe affectée à un groupe doit :

  * appartenir à la même édition que le groupe
  * appartenir au même tournoi que la sous-phase du groupe
* Une équipe ne joue que contre les équipes de son groupe.

### 2.5. Matchs (phase de groupes)

Dans une sous-phase de type “groupe” (Phase 1 et Phase 2) :

* chaque équipe affronte **exactement une fois** chaque autre équipe de son groupe
* aucun doublon A vs B
* aucun match hors groupe

---

## 3. États / statuts et transitions

### 3.1. Équipe

* `BROUILLON` :

  * peut avoir moins de 4 joueurs
  * modifiable librement
* `VALIDEE` :

  * impose 4–5 joueurs
  * utilisée pour la génération des groupes
* `ARCHIVEE` (plus tard si besoin)

Transition :

* `BROUILLON` → `VALIDEE` seulement si 4–5 joueurs

### 3.2. Phase globale

* `BROUILLON` : préparation, groupes non figés
* `OUVERTE` : phase en cours, matchs joués / scores saisis
* `CLOTUREE` : phase terminée, résultats figés

Transition :

* `BROUILLON` → `OUVERTE`
* `OUVERTE` → `CLOTUREE`

Règle associée :

* clôturer une **phase globale** clôture toutes ses **sous-phases**

### 3.3. Match

Statuts attendus (minimum) :

* `A_PLANIFIER` : créé mais pas encore affecté à un terrain/créneau
* `PLANIFIE` : terrain + créneau définis
* `TERMINE` : score validé
* `FORFAIT_A`
* `FORFAIT_B`
* `DOUBLE_FORFAIT`

---

## 4. Règles de génération

## 4.1. Génération des sous-phases (structure)

### Phase 1

Pour chaque tournoi (3) :

* 1 sous-phase `AUCUNE`

Total Phase 1 : **3 sous-phases**

### Phase 2

Pour chaque tournoi (3) :

* 1 sous-phase `CHALLENGE`
* 1 sous-phase `CONSOLANTE`

Total Phase 2 : **6 sous-phases**

### Finale

Pour chaque tournoi (3) :

* 1 finale `CHALLENGE`
* 1 finale `CONSOLANTE`

Total Finale : **6 sous-phases**

---

## 4.2. Génération des groupes

### Entrée

* une `SousPhase`
* la liste des équipes **VALIDEE** de ce tournoi et de cette édition (filtrées)
* paramètre futur : taille cible = 4 (préférée)

### Sortie

* n groupes de 3 à 5 équipes

### Règles

* Taille groupe autorisée : 3, 4 ou 5
* Objectif :

  * optimiser vers 4
  * accepter 3 ou 5 si nécessaire
* Interdiction :

  * groupe de 2
  * groupe de 6+

### Ajustements manuels autorisés

* swap d’équipes entre groupes d’une même sous-phase
* interdiction de déplacer une équipe vers un groupe d’un autre tournoi

---

## 4.3. Génération des matchs (phase de groupes)

### Entrée

* une `PhaseGlobale`
* toutes les sous-phases concernées
* tous les groupes de ces sous-phases

### Sortie

* liste de matchs sans terrain ni créneau (`A_PLANIFIER`)

### Règles strictes

Pour chaque groupe :

* toutes les paires uniques d’équipes doivent être générées une fois
* si groupe de N équipes :

  * nombre de matchs = N*(N-1)/2
* chaque match doit contenir :

  * edition
  * phase_globale
  * sous_phase
  * groupe
  * equipe_a, equipe_b
* aucun match entre deux groupes différents
* aucun doublon de paire

---

## 4.4. Génération du planning (affectation créneau/terrain)

### Contexte

* 8 terrains au total (4 intérieur, 4 extérieur)
* un créneau = 15 minutes (10 match + 5 pause)
* objectif : 8 matchs par créneau tant qu’il reste assez de matchs

### Entrée

* `PhaseGlobale`
* matchs `A_PLANIFIER`
* terrains actifs
* paramètres :

  * heure début (Edition.heure_debut)
  * durée créneau (Edition.duree_creneau_minutes)
  * règle “max 2 créneaux consécutifs par équipe” (souple mais fortement souhaitée)

### Sortie

* matchs affectés à un `Creneau` + `Terrain`
* création automatique des créneaux manquants si nécessaire

### Contraintes strictes

* une équipe ne peut pas jouer **2 matchs dans le même créneau**
* pas de doublon terrain sur un même créneau (1 match max par terrain)

### Contraintes “souples”

* une équipe ne doit pas jouer sur 3 créneaux d’affilée

  * donc max 2 consécutifs
  * mais si impossible : autorisé en dernier recours (le planning doit sortir)

### Contraintes futures (non implémentées pour l’instant)

* alternance intérieur/extérieur entre deux matchs consécutifs

  * règle existante mais **non claire**
  * moteur prévu pour l’ajouter plus tard

---

## 5. Règles de scoring

### Valeur des points classement

* Victoire = 3
* Égalité = 2
* Défaite = 1
* Forfait = 0

### Score d’un match

* points_a >= 0
* points_b >= 0

### Validation d’un score

* Un score n’impacte pas le classement tant qu’il n’est pas validé.
* La validation remplit :

  * `validated_at`
  * `validated_by`

---

## 6. Règles de classement (par groupe)

### Données calculées

Pour chaque équipe dans un groupe :

* matchs joués
* victoires / défaites / égalités
* points pour / points contre
* différence = pour - contre
* points classement (3/2/1/0)

### Tie-break (ordre strict)

En cas d’égalité de points classement :

1. Différence de points
2. Points marqués
3. Confrontation directe
4. Décision manuelle admin

---

## 7. Passage Phase 1 → Phase 2

### Objectif

Avoir environ :

* 50% Challenge
* 50% Consolante

### Entrée

* classements des groupes de Phase 1, par tournoi

### Sortie

* affectation des équipes vers :

  * Phase 2 Challenge
  * Phase 2 Consolante

### Règles

* On répartit à partir des meilleurs résultats vers Challenge
* Les autres vers Consolante
* En cas de nombre impair :

  * règle à définir (décision admin possible)

---

## 8. Phase finale (bracket)

### Décision admin

Les admins décident pour chaque tournoi et branche si la finale commence en :

* 1/8
* 1/4
* 1/2
* etc.

### Génération

* le système peut proposer une liste logique
* mais le bracket final est **validé manuellement**

---

## 9. Validation

Ce document fixe les règles.
Toute règle future doit être ajoutée ici avant implémentation.
