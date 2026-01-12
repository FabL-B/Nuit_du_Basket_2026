# 📄 `README.md`

## Nuit du Basket — API Backend

API backend Django destinée à gérer l’organisation complète de l’évènement **Nuit du Basket**, un tournoi de basket se déroulant sur une journée, avec plusieurs catégories, phases, groupes, matchs, plannings et classements.

Ce dépôt correspond **exclusivement au backend**.
Le frontend sera traité séparément.

---

## 1. Objectif du projet

L’objectif de cette API est de permettre aux **organisateurs** de :

* créer et gérer une **édition annuelle**
* inscrire des **équipes** et leurs **joueurs**
* gérer les **tournois** (Rookie / Loisir / Compétiteur)
* organiser les **phases**, **groupes**, **matchs** et **plannings**
* saisir les **scores**
* calculer automatiquement les **classements**
* préparer les **phases finales**

Le tout avec :

* des règles métier strictes
* une génération automatique contrôlée
* la possibilité d’ajustements manuels par les admins

---

## 2. Périmètre actuel

### Inclus

* Backend Django + Django REST Framework
* Base de données SQLite
* Gestion complète du tournoi côté organisation
* Tests unitaires des règles métier

### Exclu (pour l’instant)

* Frontend
* Accès joueurs / arbitres
* Authentification avancée (autre que admin)
* Export PDF / impression (prévu plus tard)

---

## 3. Architecture générale

* Framework : **Django**
* API : **Django REST Framework**
* Base de données : **SQLite**
* Langue du code métier : **français**
* Organisation modulaire par domaine métier

La description complète de l’architecture se trouve dans :

* `ARCHITECTURE.md`

---

## 3bis. Flux de génération (API admin)

La génération d’un tournoi complet suit un **pipeline strict et contrôlé**, exécuté uniquement par des administrateurs.

### Phase 1
1. Création de l’édition
2. Génération des sous-phases
3. Génération des groupes (phase 1)
4. Génération des matchs (round-robin)
5. Saisie et validation des scores
6. Clôture de la phase

### Phase 2
7. Prévisualisation de la phase 2 (calcul des qualifiés)
8. Décision admin en cas de tournoi impair (Challenge / Consolante)
9. Génération effective de la phase 2

### Planning
10. Génération du planning par phase
11. Génération du planning global à l’échelle de l’édition
    - affectation créneaux / terrains
    - gestion des pauses
    - recalcul horaire idempotent

Chaque étape est protégée par :
- des validations métier
- des garde-fous anti-régénération
- des permissions strictes

---

## 4. Documentation du projet

Les documents suivants font foi et doivent être lus dans cet ordre :

1. **`AI_GUIDE.md`**
   Règles de collaboration et cadre de travail avec l’IA

2. **`ARCHITECTURE.md`**
   Organisation technique du projet

3. **`DATA_MODEL.md`**
   Modèle de données détaillé (entités, champs, relations)

4. **`RULES_ENGINE.md`**
   Règles métier, invariants, algorithmes attendus

5. **`ROADMAP.md`**
   Avancement du projet et blocs fonctionnels

---

## 5. Structure du dépôt

```
Nuit_du_Basket_2026/
│
├── backend/
│   ├── config/          # Configuration Django
│   ├── core/            # Concepts transverses (Edition, utils)
│   ├── tournois/        # Rookie / Loisir / Compétiteur
│   ├── phases/          # Phases globales et sous-phases
│   ├── inscriptions/   # Équipes et joueurs
│   ├── groupes/         # Groupes et affectations
│   ├── matchs/          # Matchs, scores, feuilles (à venir)
│   ├── planning/        # Terrains et créneaux (à venir)
│   ├── classements/     # Classements (à venir)
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/            # Réservé au futur frontend
│
├── AI_GUIDE.md
├── ARCHITECTURE.md
├── DATA_MODEL.md
├── RULES_ENGINE.md
├── ROADMAP.md
└── README.md
```

---

## 6. Installation (backend)

### Prérequis

* Python 3.10+
* virtualenv

### Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Base de données

```bash
python manage.py migrate
```

### Lancer le serveur

```bash
python manage.py runserver
```

---

## 6bis. Exemple d’usage (admin)

Exemple de génération d’un planning global :

1. Création de l’édition
2. Génération des sous-phases
3. Génération des groupes et matchs
4. Clôture de la phase
5. Génération du planning global

```http
POST /api/admin/editions/{id}/planning-global/generer/
````

Cette action :

* planifie tous les matchs
* affecte terrains et créneaux
* applique les pauses éventuelles
* refuse toute régénération ultérieure

---

## 7. Tests

Les règles métier critiques sont couvertes par des **tests unitaires**.

Lancement des tests :

```bash
pytest
```

---

## 8. Conventions importantes

* **Une règle métier = un service**
* **Pas de logique métier dans les vues**
* **Pas de suppression destructive sans raison**
* **Statuts préférés aux deletes**
* **Code lisible avant tout**
* **Tests obligatoires pour toute règle importante**

---

## 9. Sécurité et accès

L’API distingue clairement deux niveaux :

### API admin
* Accès strictement réservé aux administrateurs
* Permissions basées sur `IsAdminUser`
* Actions sensibles protégées contre :
  - la régénération accidentelle
  - les incohérences métier
  - les appels non autorisés

### API publique (à venir)
* Lecture seule
* Aucune modification possible
* Exposition contrôlée des données (planning, résultats)s

---

## 10. État actuel du projet

Consulter :

* `ROADMAP.md`

Ce fichier indique précisément :

* ce qui est fait
* ce qui est en cours
* ce qui reste à développer

---

## 11. Évolution prévue

L’architecture permet à terme :

* ajout d’un frontend
* ajout de rôles (arbitres, tables de marque)
* export des feuilles de match
* génération avancée de planning
* montée en charge (PostgreSQL)

---

## 12. Licence

Projet développé dans un cadre personnel / associatif.
Licence à définir ultérieurement.

---

## 13. Validation

Ce README décrit l’état et l’objectif du projet à date.
