# 📄 `RULES_ENGINE.md` (mise à jour avec nouvelles règles)

Ce document formalise le **moteur de règles métier** de Nuit du Basket.
Il définit :

* invariants (règles strictes)
* règles de validation
* règles de génération (groupes, matchs, planning)
* objectifs “souples”
* extensions prévues (features futures)

---

## 1. Définitions rapides

### Edition

Évènement annuel (ex : NDB 2026) contenant tout le tournoi.

### Tournoi

Catégorie fixe : Rookie / Loisir / Compétiteur.

### Phase globale

Niveau de gestion “macro” : Phase 1 / Phase 2 / Finale.
Les opérations lourdes (génération, planning) se font **au niveau phase globale**.

### Sous-phase

Découpage d’une phase globale par :

* tournoi
* branche (`AUCUNE`, `CHALLENGE`, `CONSOLANTE`)

### Groupe

Poule d’une sous-phase.

---

## 2. Invariants (règles strictes)

### 2.1 Tournois

* Une édition contient toujours exactement **3 tournois** : `ROOKIE`, `LOISIR`, `COMPETITEUR`
* Aucun autre tournoi n’est autorisé

### 2.2 Inscription des équipes

* Une équipe appartient à **une seule édition**
* Une équipe appartient à **un seul tournoi**
* Le nom d’équipe est **unique dans l’édition** (tous tournois confondus)

### 2.3 Joueurs (règles de taille d’équipe)

Les tailles d’équipes diffèrent selon le tournoi :

* **Loisir** : **3 minimum** à **5 maximum**
* **Rookie** : **3 minimum** à **4 maximum**
* **Compétiteur** : **3 minimum** à **4 maximum**

Statut d’équipe :

* une équipe peut rester en `BROUILLON` avec un nombre de joueurs inférieur au minimum
* une équipe ne peut passer en `VALIDEE` que si elle respecte les bornes min/max de son tournoi

### 2.4 Contrôle d’âge (Rookie uniquement)

* Pour une inscription en **Rookie** : aucun joueur ne doit avoir **moins de 15 ans** à la date de l’évènement (`Edition.date_evenement`)

### 2.5 Groupes

* **Minimum 8 équipes** pour pouvoir démarrer un tournoi / une sous-phase en groupes
* **Interdiction de créer des groupes de 3 équipes**
* Une équipe affectée à un groupe doit :

  * appartenir à la même édition que le groupe
  * appartenir au même tournoi que la sous-phase du groupe

### 2.6 Matchs (phases de groupes)

Dans une sous-phase de type “phase de groupes” :

* chaque équipe affronte **exactement une fois** chaque autre équipe de son groupe
* aucun doublon A vs B
* aucun match hors groupe

---

## 3. États / statuts et transitions

### 3.1 Équipe

* `BROUILLON`
* `VALIDEE`
* `ARCHIVEE` (optionnel plus tard)

Transition :

* `BROUILLON` → `VALIDEE` seulement si :

  * le nombre de joueurs respecte les bornes du tournoi
  * et, si tournoi Rookie : tous les joueurs ont ≥ 15 ans

### 3.2 Phase globale / Sous-phase

* `BROUILLON` → `OUVERTE` → `CLOTUREE`

Règle :

* clôturer une **phase globale** clôture toutes ses **sous-phases**

Règle process (clôture) :

* une phase globale **ne peut pas être clôturée** si, dans au moins un groupe :
  * il existe une égalité entre **3 équipes ou plus** sur les critères de classement
  * et que le champ `rang_manuel` n’a pas été renseigné par un administrateur
* cette règle vise à empêcher tout départage automatique arbitraire
* le tri du classement reste consultable, mais la **clôture est bloquée**


### 3.3 Match

Statuts attendus (minimum) :

* `A_PLANIFIER`
* `PLANIFIE`
* `TERMINE`
* `FORFAIT_A`
* `FORFAIT_B`
* `DOUBLE_FORFAIT`

---

## 4. Règles de génération

## 4.1 Génération des sous-phases (structure)

### Phase 1

Pour chaque tournoi (3) :

* 1 sous-phase `AUCUNE`

### Phase 2

Pour chaque tournoi (3) :

* 1 sous-phase `CHALLENGE`
* 1 sous-phase `CONSOLANTE`

### Finale

Pour chaque tournoi (3) :

* 1 finale `CHALLENGE`
* 1 finale `CONSOLANTE`

---

## 4.2 Génération des groupes (nouvelles règles)

### Entrée

* une `SousPhase`
* liste des équipes **VALIDEE** de ce tournoi et de cette édition

### Préconditions strictes

* si nombre d’équipes < 8 : génération impossible (erreur métier)
* aucune génération ne doit produire un groupe de 3 équipes

### Sortie

* n groupes composés uniquement de tailles autorisées selon les cas ci-dessous

### Règles de découpage (strictes)

Soit N le nombre d’équipes validées pour la sous-phase :

* **N = 8** → 2 groupes de 4
* **N = 9** → 1 groupe de 4 et 1 groupe de 5
* **N = 10** → 2 groupes de 5
* **N = 11** → **inscriptions bloquées à 10** : la 11e équipe doit être **refusée** tant qu’une 12e équipe ne s’est pas inscrite
  (objectif : éviter 3/3/5 ou autres répartitions interdites)
* **N ≥ 12** → groupes de **4 et 5** uniquement, en favorisant 4 quand possible, sans jamais créer de 3

### Ajustements manuels autorisés

* swap d’équipes entre groupes d’une même sous-phase
* interdiction de déplacer une équipe vers un groupe d’un autre tournoi

---

## 4.3 Génération des matchs (phase de groupes)

### Entrée

* une `PhaseGlobale`
* toutes les sous-phases concernées
* tous les groupes de ces sous-phases

### Sortie

* liste de matchs `A_PLANIFIER` (sans terrain ni créneau)

### Règles strictes

Pour chaque groupe :

* générer toutes les paires uniques d’équipes exactement une fois
* aucun match entre deux groupes différents
* aucun doublon de paire

---

## 4.4 Génération du planning (créneaux + terrains)

### Contexte

* 8 terrains : 4 intérieur, 4 extérieur
* créneau standard : 15 minutes (10 match + 5 pause)
* objectif : 8 matchs par créneau tant qu’il reste assez de matchs

### Contraintes strictes

* une équipe ne peut pas jouer 2 matchs dans le même créneau
* un terrain ne peut accueillir qu’un seul match par créneau

### Contraintes souples (à faire au mieux)

1. **Répartition intérieur / extérieur**

* objectif : une équipe doit jouer **autant que possible** un nombre similaire de matchs en intérieur et extérieur

2. **Éviter deux matchs d’affilée**

* objectif : autant que possible, une équipe ne doit pas enchaîner deux matchs consécutifs
* justification métier : après un match, l’équipe peut aider à la table/arbitrage du match suivant sur le terrain

⚠️ Pour l’instant :

* tables/arbitres ne sont pas gérés par le système
* mais le planning doit rester compatible avec une feature future

### Règle existante conservée (souple)

* éviter 3 créneaux d’affilée (max 2 consécutifs), mais la planification doit toujours sortir même en dernier recours

---

## 4.5 Créneaux spéciaux : pauses nommées (nouvelle règle)

### Objectif

Permettre d’insérer une ou plusieurs pauses dans le planning, par exemple :

* à 15h00 : pause “Concours de shoot” de 1h ou 2h
* reprise des matchs à 16h ou 17h

### Règle

* Une pause est un intervalle de temps où :

  * aucun match ne doit être planifié
  * tous les créneaux pendant la pause sont considérés comme “bloqués”
* Une édition peut contenir **plusieurs pauses**
* Ces pauses décalent mécaniquement les matchs qui auraient dû se jouer pendant cet intervalle

### Statut

* règle métier validée
* nécessite une modélisation dédiée (concept de “pause / évènement planning”) avant implémentation

---

## 5. Règles de scoring (inchangé)

### Points de classement

* Victoire = 3
* Égalité = 2
* Défaite = 1
* Forfait = 0

### Validation

* le classement est recalculé uniquement à la validation d’un score

---

## 6. Classement (inchangé)

Tie-break :

Tie-break :

1. Différence de points
2. Points marqués
3. Confrontation directe (uniquement en cas d’égalité à 2 équipes)
4. Décision manuelle admin (obligatoire en cas d’égalité à ≥3 équipes)

⚠️ En cas d’égalité à ≥3 équipes, l’absence de décision manuelle bloque la clôture de la phase.

---

## 7. Passage Phase 1 → Phase 2 (inchangé à ce stade)

Objectif : 50% Challenge / 50% Consolante (au mieux)

---

## Historique

### 2026-01-07

#### Règles (spécifications figées)
- Groupes : minimum 8 équipes, aucun groupe de 3.
- Répartition :
  - 9 équipes → 2 groupes (4 et 5)
  - 10 équipes → 2 groupes (5 et 5)
  - 11 équipes → inscriptions bloquées tant qu’une 12e équipe n’est pas inscrite (pas de groupe de 3).
  - ≥12 équipes → groupes de 4 et/ou 5 (au mieux).
- Tailles d’équipes (inscription) :
  - Loisir : 3 à 5 joueurs
  - Rookie & Compétiteur : 3 à 4 joueurs
- Rookie : contrôle d’âge à l’inscription/validation équipe (≥ 15 ans).
- Planning (objectifs souples) :
  - équilibrage intérieur / extérieur “au mieux”
  - éviter les matchs d’affilée “au mieux”
- Planning : ajout de pauses nommées (ex: concours de shoot) décalant les matchs après la pause.

#### Implémentations (backend)
- Validation équipe : bornes min/max par tournoi + contrôle d’âge Rookie (≥ 15 ans).
- Sous-phases : génération automatique (P1 = 3, P2 = 6, Finale = 6).
- Groupes : génération automatique v2 (min 8, groupes 4/5 uniquement, cas 8/9/10/11 gérés).
- Groupes : échange manuel (swap) entre deux équipes de deux groupes de la même sous-phase.
- Matchs : génération automatique par phase globale (tous tournois confondus).
- Feuille de match : `MatchSheet` (1–1) + `sheet_code` UUID.
- Scores : `Score` (1–1), validation verrouillante, passage match → `TERMINE`.
- Classement : recalcul automatique à validation d’un score.
- Planning :
  - génération créneaux + affectation terrain/créneau (contraintes strictes)
  - heuristiques améliorées (enchaînements + équilibrage I/E) + métriques
  - pauses nommées + recalcul des débuts de créneaux

### 2026-01-07

- Tie-breaks implémentés (points/diff/points marqués/confrontation directe/manuel)
- Tie-break : confrontation directe uniquement pour égalité à 2 équipes ; égalité à ≥3 équipes → départage manuel.

### 2026-01-08

- Clôture de phase : blocage obligatoire si égalité à ≥3 équipes sans `rang_manuel` (règle process).
