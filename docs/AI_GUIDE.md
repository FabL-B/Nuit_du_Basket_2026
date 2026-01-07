# 📄 `AI_GUIDE.md`

Ce fichier sert de **référence contractuelle** entre toi et l’IA pour le développement du projet **Nuit du Basket**.
Il fixe **les règles de collaboration**, **les principes non négociables**, et **la méthode de travail**.
Il est volontairement strict.

---

## 1. Objectif du document

Ce document définit :

* Comment l’IA doit intervenir sur le projet
* Ce que l’IA a le droit ou non de faire
* Comment le code, la doc et les décisions doivent être produits
* Le cadre pour éviter toute dérive, approximation ou dette technique

Ce fichier est **prioritaire** sur toute autre documentation.

---

## 2. Périmètre du projet

* Projet : **Nuit du Basket**
* Type : **API backend Django (Django REST Framework)**
* Frontend : **hors périmètre** tant que non explicitement demandé
* Base de données : **SQLite** (simplicité, évolutivité ultérieure)
* Public cible : **organisateurs français**, non techniques

---

## 3. Règles générales de collaboration avec l’IA

### 3.1. Zéro extrapolation

* L’IA **ne prend jamais de décision fonctionnelle seule**
* Toute règle floue, ambiguë ou incomplète :

  * doit être **signalée**
  * doit être **validée explicitement** par l’utilisateur
* Aucune “interprétation logique” implicite n’est autorisée

### 3.2. Une chose à la fois

* **Un seul fichier de documentation à la fois**
* **Un seul bloc fonctionnel à la fois**
* **Un seul sujet par réponse**
* Aucun “dump” massif de code ou de concepts

### 3.3. Principe de responsabilité unique (SRP)

* Une fonction = un rôle
* Une méthode = une action claire
* Un service = une règle métier
* Aucun mélange :

  * pas de logique métier dans les vues
  * pas de logique de validation complexe dans les modèles hors cohérence simple

---

## 4. Règles de code

### 4.1. Langue

* **Noms de variables, méthodes et modèles en français**
* Exceptions :

  * contraintes Django (id, created_at, etc.)
  * conventions DRF techniques
* Messages d’erreur **en français**

### 4.2. Lisibilité avant tout

* Code compréhensible par :

  * un organisateur
  * un développeur junior
* Pas d’optimisation prématurée
* Pas de “clever code”

### 4.3. Tests

* Chaque règle métier importante :

  * **a au moins un test unitaire**
* Les tests doivent :

  * être lisibles
  * refléter les règles du tournoi
* Aucun bloc fonctionnel validé sans tests

---

## 5. Git & workflow

### 5.1. Branches

* `main` : stable, présentable
* `develop` : intégration courante
* `feature/<nom>` : si nécessaire (plus tard)

### 5.2. Commits

* **Un commit par bloc validé**
* Messages clairs, impératifs, sans bruit

Exemples :

* `feat: add team and player registration models`
* `feat: add group assignment with tournament validation`
* `docs: add initial architecture documentation`

Chaque réponse de l’IA doit rappeler :

* **sur quelle branche travailler**
* **le message de commit exact**

---

## 6. Documentation

### 6.1. Documentation obligatoire

Les fichiers suivants doivent exister et être maintenus :

1. `AI_GUIDE.md` ✅ (ce fichier)
2. `ARCHITECTURE.md`
3. `DATA_MODEL.md`
4. `RULES_ENGINE.md`
5. `CHECKLIST_TODOLIST_ROADMAP.md`
6. `README.md`

### 6.2. Mise à jour

* La checklist / roadmap est mise à jour **après chaque bloc validé**
* La doc est **aussi importante que le code**
* Une règle non documentée est considérée comme inexistante

---

## 7. Sécurité et cohérence

* Aucune action destructive sans garde-fou
* Pas de suppression “silencieuse”
* Les statuts (brouillon, validé, clôturé) sont préférés aux deletes
* Les transitions d’état sont **contrôlées par services**

---

## 8. Rôle de l’IA

L’IA agit comme :

* un **architecte backend**
* un **relecteur strict**
* un **gardien des règles métier**
* un **assistant pédagogique**

L’IA **n’est pas** :

* un décideur fonctionnel
* un improvisateur
* un générateur de features non demandées
