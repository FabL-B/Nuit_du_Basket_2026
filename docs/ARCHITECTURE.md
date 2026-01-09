# 📄 `ARCHITECTURE.md`

Ce document décrit **l’architecture technique et logique** de l’application **Nuit du Basket**.
Il explique **comment le projet est structuré**, **pourquoi**, et **comment les différentes briques interagissent**.

Ce document est **référentiel** : toute évolution devra rester cohérente avec lui (ou le faire évoluer explicitement).

---

## 1. Vue d’ensemble

### Type d’application

* **API backend Django**
* Framework : **Django + Django REST Framework**
* Base de données : **SQLite**
* Frontend : **hors périmètre** pour l’instant

### Objectif de l’architecture

* Clarté
* Évolutivité
* Séparation stricte des responsabilités
* Respect des règles métier complexes du tournoi

---

## 2. Organisation des dossiers

À la racine du projet :

```
Nuit_du_Basket_2026/
│
├── backend/
│   ├── config/              # Configuration Django (settings, urls, wsgi, asgi)
│   ├── core/                # Concepts transverses (Edition, healthcheck, utils globaux)
│   ├── tournois/            # Gestion des tournois (Rookie / Loisir / Compétiteur)
│   ├── phases/              # Phases globales et sous-phases
│   ├── inscriptions/        # Équipes et joueurs
│   ├── groupes/             # Groupes et affectation des équipes
│   ├── matchs/              # Matchs, scores, feuilles de match (à venir)
│   ├── planning/            # Créneaux et terrains (à venir)
│   ├── classements/         # Classements (à venir)
│   ├── .venv/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                # Réservé au futur front
└── README.md
```

---

## 3. Principe fondamental : séparation des couches

Chaque app respecte **strictement** les couches suivantes :

### 3.1. Modèles (`models.py`)

* Représentation des données
* Contraintes simples (unicité, cohérence FK)
* **Pas de logique métier complexe**
* `clean()` autorisé uniquement pour cohérence locale

### 3.2. Services (`services.py`)

* **Cœur des règles métier**
* Transitions d’état (validation, clôture, génération)
* Opérations complexes (génération de groupes, matchs, classements)
* Transaction atomique si nécessaire

👉 **Toute règle du tournoi vit ici**

### 3.3. API / Views (`views.py`)

* Exposition des endpoints
* Authentification / permissions
* Appel des services
* **Aucune logique métier**

### 3.4. Sérialiseurs (`serializers.py`)

* Validation des données entrantes
* Mapping JSON ↔ modèles
* Pas de règles métier lourdes

### 3.5. Tests (`tests/`)

* Tests unitaires des services
* Tests des contraintes critiques
* Lisibles, proches du langage métier

## 3.6. API Admin

L’application expose une API d’administration dédiée (`/api/admin/`).

Caractéristiques :
- Réservée aux utilisateurs staff
- Accès via Django REST Framework
- Actions métier explicites (générer, valider, clôturer, swap, forfait)

Les endpoints admin :
- n’implémentent aucune règle métier
- délèguent systématiquement aux services
- servent de couche de pilotage fonctionnel

## 3.7. Règles métier vs règles de process

- Les règles métier définissent ce qui est vrai dans le tournoi.
- Les règles de process définissent ce qui est autorisé à un instant donné.

Les règles de process :
- peuvent évoluer
- sont souvent appliquées lors d’actions (clôture, génération)
- ne modifient pas le modèle de données

---

## 4. Concepts métier principaux

### 4.1. Edition

* Une **édition annuelle** de la Nuit du Basket
* Racine de presque toutes les données
* Contient :

  * tournois
  * phases
  * équipes
  * terrains
  * créneaux

---

### 4.2. Tournois

* Toujours exactement **3 tournois par édition** :

  * Rookie
  * Loisir
  * Compétiteur
* Pas de création libre de nouveaux types
* Identifiés par un **code** stable

---

### 4.3. Phases (concept clé)

#### Phase globale

* Phase 1
* Phase 2
* Phase finale

Une **phase globale** regroupe plusieurs sous-phases.

#### Sous-phase

* Liée à :

  * une phase globale
  * un tournoi
  * une branche (challenge / consolante)
* Exemple :

  * Phase 2 – Rookie – Challenge
  * Phase 2 – Loisir – Consolante

👉 Les actions lourdes (génération groupes, matchs, planning) se font **au niveau phase globale**, pas sous-phase par sous-phase.

---

### 4.4. Inscriptions

#### Équipe

* Liée à :

  * une édition
  * un tournoi
* Nom unique par édition
* Statuts :

  * BROUILLON
  * VALIDEE
  * ARCHIVEE

#### Joueur

* Toujours rattaché à une équipe
* Une équipe validée doit contenir **4 à 5 joueurs**

---

### 4.5. Groupes

* Un groupe appartient à **une sous-phase**
* Contient plusieurs équipes
* Une équipe :

  * appartient à **un seul groupe par sous-phase**
  * ne peut jamais changer de tournoi

Les modifications manuelles sont possibles mais **strictement contrôlées**.

---

## 5. Génération automatique (vision globale)

### 5.1. Groupes

* Générés à partir des équipes validées
* Par sous-phase
* La taille des groupes est définie précisément dans `RULES_ENGINE.md`.
* Génération automatique + ajustement manuel possible

### 5.2. Matchs

* Générés **par phase globale**
* En tenant compte de :

  * tous les groupes
  * tous les tournois
* Règle stricte :

  * chaque équipe affronte exactement une fois chaque autre équipe de son groupe

### 5.3. Planning

* Affectation des matchs à :

  * créneaux
  * terrains
* Contraintes :

  * 8 matchs par créneau (si possible)
  * max 2 créneaux consécutifs par équipe
  * extensible (changement intérieur/extérieur plus tard)

---

## 6. Sécurité et permissions

* Accès réservé aux **admins**
* Permission globale :

  * `IsAdminUser`
* Aucune écriture publique
* Toutes les actions critiques passent par des services

---

## 7. Évolutivité prévue

Cette architecture permet sans refonte majeure :

* ajout d’un frontend
* passage à PostgreSQL
* ajout de rôles (arbitres, table de marque)
* ajout de règles supplémentaires
* export PDF / impression

---

## 8. Ce que l’architecture interdit volontairement

* Logique métier dans les vues
* Couplage fort entre apps
* Suppressions destructrices non contrôlées
* Génération “tournoi par tournoi”
* Décisions implicites

---

## 9. Validation

Ce document est valide tant qu’aucune règle structurante ne le contredit.

## 10. Points volontairement non finalisés

Certaines règles sont volontairement laissées ouvertes :
- passage Phase 1 → Phase 2 en cas d’effectif impair
- arbitrage admin pour certaines décisions

Ces règles seront définies avant implémentation définitive.
