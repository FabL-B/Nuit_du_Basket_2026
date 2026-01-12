# API_REFERENCE.md

Ce document liste les **endpoints actuels** et les **endpoints prévus** de l’API *Nuit du Basket*.

* Base API (actuelle) : `/api/admin/`
* Public : **non implémenté** (backend uniquement pour le moment)

## Conventions

### Admin
* Tous les endpoints `/api/admin/*` sont **réservés aux admins** (permission : `IsAdminUser` / `is_staff=True`).
* Auth affichée dans Swagger : Session + Basic (par défaut DRF).

### Public
* Tous les endpoints `/api/public/*` sont **publics** :
  * `permission_classes = [AllowAny]`
  * `authentication_classes = []` (Swagger ne doit pas afficher Basic/Session sur le public)
* Par défaut, quand `edition` n’est pas fournie, les endpoints public prennent la **dernière édition** (par `date_evenement`).

### Général
* La logique métier se trouve dans des **services** (pas dans les views).
* Les endpoints marqués **En pause** ne doivent pas être implémentés tant que les règles métier associées ne sont pas figées.

## Statuts

* **Implémenté** : endpoint existant
* **Prévu** : endpoint à venir
* **En pause** : bloqué tant que les règles ne sont pas figées

---

# A) API PUBLIC

## A1 Éditions (metadata)

### GET `/api/public/editions/`
* Rôle : lister les éditions (tri : `-date_evenement`, `-id`)
* Statut : **Implémenté**

### GET `/api/public/editions/{id}/`
* Rôle : détail d’une édition
* Statut : **Implémenté**

---

## A2 Terrains (metadata)

### GET `/api/public/terrains/`
* Rôle : lister les terrains de l’édition (dernière édition par défaut)
* Query params :
  * `edition` (int, optionnel) : ID édition
  * `actif` (bool, optionnel) : par défaut `true` (ne renvoie que les terrains actifs)
* Statut : **Implémenté**

### GET `/api/public/terrains/{id}/`
* Rôle : détail d’un terrain
* Statut : **Implémenté**

---

## A3 Tournois

### GET `/api/public/tournois/`
* Rôle : lister les tournois de l’édition (dernière édition par défaut)
* Query params :
  * `edition` (int, optionnel)
* Statut : **Implémenté**

### GET `/api/public/tournois/{id}/`
* Rôle : détail d’un tournoi
* Statut : **Implémenté**

---

## A4 Groupes

### GET `/api/public/groupes/`
* Rôle : lister les groupes de l’édition (dernière édition par défaut)
* Query params :
  * `edition` (int, optionnel)
  * `tournoi` / `tournoi_code` (str, optionnel)
  * `phase` (str, optionnel) : `type_phase` de la phase globale
  * `branche` (str, optionnel)
* Statut : **Implémenté**

### GET `/api/public/groupes/{id}/`
* Rôle : détail d’un groupe (serializer détail)
* Statut : **Implémenté**

---

## A5 Planning (matchs planifiés)

### GET `/api/public/planning/`
* Rôle : lister les matchs planifiés (créneau + terrain) (dernière édition par défaut)
* Query params :
  * `edition` (int, optionnel)
  * `tournoi` / `tournoi_code` (str, optionnel)
  * `phase` (str, optionnel)
  * `groupe` (int, optionnel)
  * `terrain` (int, optionnel)
* Statut : **Implémenté**

### GET `/api/public/planning/{id}/`
* Rôle : détail d’un match planifié
* Statut : **Implémenté**

---

## A6 Résultats (matchs terminés et validés)

### GET `/api/public/resultats/`
* Rôle : lister les matchs **validés** (score présent + `valide_le` non nul) (dernière édition par défaut)
* Query params :
  * `edition` (int, optionnel)
  * `tournoi` / `tournoi_code` (str, optionnel)
  * `phase` (str, optionnel)
  * `groupe` (int, optionnel)
* Statut : **Implémenté**

### GET `/api/public/resultats/{id}/`
* Rôle : détail d’un match validé
* Statut : **Implémenté**

---

# B) API ADMIN

## B1 Éditions

### GET `/api/admin/editions/`
* Rôle : lister les éditions
* Statut : **Implémenté**

### POST `/api/admin/editions/`
* Rôle : créer une édition
* Statut : **Implémenté**

### GET `/api/admin/editions/{id}/`
* Rôle : lire une édition
* Statut : **Implémenté**

### PUT/PATCH `/api/admin/editions/{id}/`
* Rôle : modifier une édition
* Statut : **Implémenté**
* Note (future règle process) : certaines modifications pourront être bloquées quand le tournoi a démarré

### DELETE `/api/admin/editions/{id}/`
* Rôle : supprimer une édition
* Statut : **Implémenté**
* Note (future règle process) : suppression probablement interdite après inscriptions/matchs

### POST `/api/admin/editions/{id}/planning-global/generer/`
* Rôle : générer le planning global d’une édition (phase1 obligatoire, phase2 et finale optionnelles)
* Body : `phase1_id` (obligatoire), `phase2_id` (optionnel), `phase_finale_id` (optionnel), options concours
* Statut : **Implémenté**

---

## B2 Tournois (Rookie / Loisir / Compétiteur)

### GET `/api/admin/tournois/`
* Rôle : lister les tournois
* Statut : **Implémenté**

### POST `/api/admin/tournois/`
* Rôle : créer un tournoi
* Statut : **Implémenté** *(si tu gardes `ModelViewSet` côté admin)*

### GET `/api/admin/tournois/{id}/`
* Rôle : lire un tournoi
* Statut : **Implémenté**

### PUT/PATCH `/api/admin/tournois/{id}/`
* Rôle : modifier un tournoi (ex: libellé)
* Statut : **Implémenté**

### DELETE `/api/admin/tournois/{id}/`
* Rôle : supprimer un tournoi
* Statut : **Implémenté** *(si tu gardes `ModelViewSet` côté admin)*

> Note métier : tu peux décider plus tard de verrouiller `create/delete` si tu veux imposer “toujours 3 tournois fixes”.

---

## B3 Phases globales

### GET `/api/admin/phases-globales/`
* Rôle : lister les phases globales
* Statut : **Implémenté**

### POST `/api/admin/phases-globales/`
* Rôle : créer une phase globale
* Statut : **Implémenté**

### GET `/api/admin/phases-globales/{id}/`
* Rôle : lire une phase globale
* Statut : **Implémenté**

### PUT/PATCH `/api/admin/phases-globales/{id}/`
* Rôle : modifier une phase globale
* Statut : **Implémenté**

### DELETE `/api/admin/phases-globales/{id}/`
* Rôle : supprimer une phase globale
* Statut : **Implémenté**

### POST `/api/admin/phases-globales/{id}/generer-sous-phases/`
* Rôle : générer les sous-phases d’une phase globale
* Statut : **Implémenté**

### POST `/api/admin/phases-globales/{id}/generer-matchs/`
* Rôle : générer tous les matchs d’une phase globale (tous groupes/tournois confondus)
* Statut : **Implémenté**

### POST `/api/admin/phases-globales/{id}/generer-planning/`
* Rôle : générer le planning d’une phase globale (créneaux + terrains)
* Statut : **Implémenté**

### POST `/api/admin/phases-globales/{id}/cloturer/`
* Rôle : clôturer une phase globale
* Statut : **Implémenté**

### GET `/api/admin/phases-globales/{id}/phase2-preview/`
* Rôle : prévisualiser la phase 2 depuis une phase 1 (sans créer/modifier)
* Statut : **Implémenté**

### POST `/api/admin/phases-globales/{id}/phase2-generer/`
* Rôle : générer la phase 2 depuis une phase 1 (avec décision si impair)
* Statut : **Implémenté** *(si tes règles sont validées — sinon marque “En pause”)*

---

## B4 Sous-phases

### GET `/api/admin/sous-phases/`
* Rôle : lister les sous-phases
* Statut : **Implémenté**

### GET `/api/admin/sous-phases/{id}/`
* Rôle : lire une sous-phase
* Statut : **Implémenté**

### POST `/api/admin/sous-phases/{id}/generer-groupes-phase1/`
* Rôle : générer les groupes + affectations équipes (phase 1) pour une sous-phase
* Statut : **Implémenté**

---

## B5 Groupes

### GET `/api/admin/groupes/`
* Rôle : lister les groupes
* Query params :
  * `phase_globale` (int, optionnel)
  * `sous_phase` (int, optionnel)
  * `tournoi` (int, optionnel)
* Statut : **Implémenté**

### POST `/api/admin/groupes/`
* Rôle : créer un groupe
* Statut : **Implémenté**

### GET `/api/admin/groupes/{id}/`
* Rôle : lire un groupe
* Statut : **Implémenté**

### PUT/PATCH `/api/admin/groupes/{id}/`
* Rôle : modifier un groupe
* Statut : **Implémenté**

### DELETE `/api/admin/groupes/{id}/`
* Rôle : supprimer un groupe
* Statut : **Implémenté**

### POST `/api/admin/groupes/swap-equipes/`
* Rôle : interchanger deux équipes entre deux groupes
* Statut : **Implémenté**

---

## B6 Matchs

### GET `/api/admin/matchs/`
* Rôle : lister les matchs
* Query params :
  * `edition` (int), `phase_globale` (int), `sous_phase` (int), `tournoi_code` (str),
  * `groupe` (int), `terrain` (int), `creneau` (int), `statut` (str)
* Statut : **Implémenté**

### GET `/api/admin/matchs/{id}/`
* Rôle : lire un match
* Statut : **Implémenté**

### POST `/api/admin/matchs/{id}/feuille/`
* Rôle : créer ou récupérer la feuille de match (idempotent)
* Statut : **Implémenté**

### POST `/api/admin/matchs/{id}/score/`
* Rôle : saisir un score (non validé)
* Statut : **Implémenté**

### POST `/api/admin/matchs/{id}/score/valider/`
* Rôle : valider le score (verrouillage, statut match, recalcul éventuel)
* Statut : **Implémenté**

### POST `/api/admin/matchs/swap-planning/`
* Rôle : swap des affectations planning entre deux matchs
* Statut : **Implémenté**

### POST `/api/admin/matchs/{id}/forfait/`
* Rôle : déclarer un forfait
* Statut : **Implémenté**

---

# C Roadmap (prévu / en pause)

## C1 Inscriptions : équipes et joueurs
* `/api/admin/equipes/` CRUD + `valider/` : **Prévu**
* `/api/admin/joueurs/` CRUD : **Prévu**

## C2 Planning / pauses / créneaux (admin)
* `/api/admin/creneaux/` : **Prévu**
* `/api/admin/terrains/` : **Prévu**
* `/api/admin/pauses-planning/` CRUD : **Prévu**

## C3 Classements
* `/api/admin/groupes/{id}/classement/` : **Prévu**
* `/api/admin/classements/{id}/rang-manuel/` : **Prévu**

---

## OpenAPI / Swagger (documentation auto)

Si `drf-spectacular` est activé :

* Schéma OpenAPI (YAML/JSON) : `/api/schema/`
* Swagger UI : `/api/docs/`

---

## Historique

* 2026-01-07 : inventaire initial des endpoints admin
* 2026-01-12 : ajout des endpoints public + mise à jour inventaire admin (phases, sous-phases, forfait, swap planning, planning global)
