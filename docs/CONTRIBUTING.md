# Contribuer au projet Nuit du Basket

Ce document définit les règles de contribution au projet, en particulier la
convention de nommage des commits Git.

L’objectif est d’avoir :
- un historique Git lisible
- des commits compréhensibles sans ouvrir le code
- une séparation claire entre fonctionnel, technique et documentation

---

## Convention de commits

Chaque commit **DOIT** respecter le format suivant :

<type>: <message court en anglais>

Exemple :
feat: generate matches for global phase

---

## Types de commits autorisés

### feat
Ajout d’une nouvelle fonctionnalité métier ou technique.

Exemples :
- feat: add automatic group generation
- feat: generate planning for global phase
- feat: add named pauses in planning

---

### fix
Correction d’un bug existant.

Exemples :
- fix: prevent team from playing twice in same timeslot
- fix: validate score before recalculating standings

---

### refactor
Modification interne du code **sans changement fonctionnel**.

Exemples :
- refactor: split planning logic into dedicated services
- refactor: simplify group generation algorithm

---

### style
Changements purement cosmétiques (formatage, linting).

Exemples :
- style: format code with black
- style: apply black and ruff formatting

Aucun changement de logique ne doit être inclus dans un commit `style`.

---

### test
Ajout ou modification de tests.

Exemples :
- test: add tests for planning heuristics
- test: cover edge cases for team validation

---

### docs
Documentation uniquement.

Exemples :
- docs: update project documentation after backend implementation
- docs: update rules engine history
- docs: update data model documentation

---

### chore
Tâches techniques non fonctionnelles.

Exemples :
- chore: add gitignore
- chore: configure black and ruff
- chore: update dependencies

---

## Règles importantes

- Un commit = un objectif clair
- Ne pas mélanger :
  - code fonctionnel + formatage
  - code + documentation
- Le message doit être :
  - court
  - à l’infinitif
  - sans point final

---

## Langue

- Messages de commit : **anglais**
- Code (noms de variables, classes) : **français**
- Documentation : **français**

---

## Branches

- `main` : stable / livrable
- `develop` : intégration continue
- branches de travail :
  - `feat/<nom>`
  - `fix/<nom>`
  - `refactor/<nom>`

Exemple :
feat/planning-pauses

---

## Formatage et qualité

Avant chaque push :
- Black doit passer
- Ruff doit passer
- Les tests doivent être verts

Un push bloqué par Black ou Ruff est volontaire.
