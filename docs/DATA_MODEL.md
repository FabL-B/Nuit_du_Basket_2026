# 📄 `DATA_MODEL.md` (mise à jour)

Cette version **met à jour le modèle de données** pour intégrer **strictement** les nouvelles règles validées, **sans implémentation prématurée**.

Les ajouts concernent :

* tailles d’équipes par tournoi
* contrôle d’âge en Rookie
* règles de groupes (min 8, pas de groupes de 3)
* préparation du modèle pour les **pauses nommées dans le planning**

---

## 1. Principes généraux (inchangé)

* Le modèle de données **n’implémente pas toute la logique métier**.
* Les règles complexes restent dans les **services**.
* Le modèle garantit :

  * la cohérence
  * les contraintes structurelles
  * les garde-fous impossibles à violer silencieusement.

---

## 2. Modèles existants impactés

---

## 2.1 `inscriptions.Equipe` (mise à jour des règles)

### Champs (inchangé)

* `edition` (FK → Edition)
* `tournoi` (FK → Tournoi)
* `nom`
* `nom_club`
* `statut` (`BROUILLON`, `VALIDEE`, `ARCHIVEE`)
* `cree_le`, `modifie_le`

### Contraintes (inchangé)

* unicité (`edition`, `nom`)
* cohérence édition / tournoi

### Règles métier associées (clarifiées)

Ces règles **ne sont pas des contraintes DB**, mais doivent être appliquées **au moment de la validation** :

| Tournoi     | Joueurs min | Joueurs max |
| ----------- | ----------- | ----------- |
| Loisir      | 3           | 5           |
| Rookie      | 3           | 4           |
| Compétiteur | 3           | 4           |

* Une équipe peut exister en `BROUILLON` avec un nombre de joueurs inférieur au minimum.
* Le passage en `VALIDEE` est **refusé** si les bornes ne sont pas respectées.

---

## 2.2 `inscriptions.Joueur` (règle d’âge Rookie)

### Champs (inchangé)

* `equipe` (FK → Equipe)
* `prenom`
* `nom`
* `date_naissance`
* `email`
* `telephone`
* `cree_le`, `modifie_le`

### Règle métier associée (nouvelle)

* Si l’équipe est inscrite en **Rookie** :

  * l’âge du joueur à la date `Edition.date_evenement` doit être **≥ 15 ans**
* Cette règle :

  * n’est **pas** une contrainte DB
  * est vérifiée lors de la **validation de l’équipe**

---

## 2.3 `groupes.Groupe` (règles renforcées)

### Champs (inchangé)

* `sous_phase` (FK → SousPhase)
* `code`
* `cree_le`, `modifie_le`

### Contraintes DB (inchangé)

* unicité (`sous_phase`, `code`)

### Règles métier associées (clarifiées)

* La génération automatique des groupes :

  * est **interdite** si le nombre d’équipes < 8
  * ne doit **jamais produire de groupe de 3 équipes**
* Les tailles autorisées sont **4 et 5 uniquement**
* Cas particulier :

  * à 11 équipes → l’inscription de la 11e équipe doit être **refusée** tant qu’une 12e équipe ne s’est pas inscrite

---

## 2.4 `groupes.GroupeEquipe` (inchangé structurellement)

### Champs

* `groupe` (FK → Groupe)
* `equipe` (FK → Equipe)
* `seed` (nullable)
* `cree_le`

### Contraintes DB

* unicité (`groupe`, `equipe`)
* unicité (`groupe`, `seed`) si renseigné

### Validations métier (rappel)

* `equipe.edition` == `groupe.sous_phase.phase_globale.edition`
* `equipe.tournoi` == `groupe.sous_phase.tournoi`

---

## 3. Modèles liés au planning (préparation aux nouvelles règles)

Les règles de **pauses nommées** nécessitent une évolution du modèle.

⚠️ **Aucune implémentation immédiate** : on prépare le terrain.

---

## 3.1 Nouveau concept à prévoir : `PlanningPause` (futur)

### Rôle

Représenter une pause planifiée dans le déroulé du tournoi (ex : concours de shoot).

### Champs proposés (non implémentés)

* `edition` (FK → Edition)
* `nom` (ex : "Concours de shoot")
* `debut` (DateTimeField)
* `fin` (DateTimeField)
* `cree_le`

### Règles associées

* Aucun match ne peut être planifié dans l’intervalle `[debut, fin)`
* Les créneaux concernés sont considérés comme **bloqués**
* Une édition peut avoir **plusieurs pauses**

👉 Le moteur de planning devra **consommer ces pauses** pour décaler automatiquement les matchs.

---

## 4. Modèles `Match`, `Terrain`, `Creneau` (impact règles souples)

### Aucun champ supplémentaire requis pour l’instant.

Les règles suivantes restent **métier uniquement** :

* équilibrage intérieur / extérieur
* éviter les matchs consécutifs
* éviter plus de 2 créneaux consécutifs

Ces règles seront implémentées **dans le service de génération de planning**, pas au niveau DB.

---

## 5. Ce qui est volontairement NON mis en base

* règles de calcul des groupes
* règles d’équilibrage indoor/outdoor
* arbitrage / table de marque
* refus de la 11e équipe (logique d’inscription, pas structurelle)

---

## Historique

* 2026-01-07 :
  Mise à jour des règles de tailles d’équipes par tournoi, ajout du contrôle d’âge Rookie (≥15 ans), clarification des règles de groupes (min 8 équipes, pas de groupes de 3, cas 11 équipes), et préparation du modèle pour les pauses nommées dans le planning.
  Score (1–1), validation verrouillante, match terminé
  Classement + recalcul auto à validation score
  Créneaux/Terrains utilisés pour planifier les matchs (creneau/terrain nullable au départ)
  “PausePlanning (edition, nom, debut, duree_minutes, est_active)