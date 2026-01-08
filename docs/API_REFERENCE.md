Très bien.
Voici **une documentation API claire, exhaustive et structurée**, listant **les endpoints existants** et **ceux prévus**, sans ambiguïté sur l’état d’avancement.

👉 Ce document est conçu pour devenir **`API_REFERENCE.md`** (ou `API_ENDPOINTS.md` si tu préfères).

---

# 📡 API Nuit du Basket – Référence des endpoints

Base URL (actuelle) :

```
/api/admin/
```

⚠️ Tous les endpoints listés ici sont **réservés aux admins** (`is_staff=True`).

---

## 1. Éditions

### ✅ GET /api/admin/editions/

Lister toutes les éditions.

**Statut :** implémenté
**Permissions :** admin
**Réponse :**

* id
* nom
* date_evenement
* heure_debut
* duree_creneau_minutes
* cree_le
* modifie_le

---

### ✅ POST /api/admin/editions/

Créer une édition.

**Statut :** implémenté
**Payload :**

```json
{
  "nom": "NDB 2026",
  "date_evenement": "2026-06-20",
  "heure_debut": "14:00",
  "duree_creneau_minutes": 15
}
```

---

### 🔜 PUT /api/admin/editions/{id}/

Modifier une édition.

**Statut :** prévu
⚠️ À bloquer si tournoi déjà lancé (règle future)

---

## 2. Tournois (Rookie / Loisir / Compétiteur)

### ✅ GET /api/admin/tournois/

Lister les tournois d’une édition.

**Statut :** implémenté
**Champs :**

* id
* edition
* code (`ROOKIE`, `LOISIR`, `COMPETITEUR`)
* libelle

---

### 🔜 PUT /api/admin/tournois/{id}/

Modifier libellé / activation.

**Statut :** prévu
⚠️ Les codes sont **figés** (pas de CRUD libre)

---

## 3. Équipes & joueurs

### 🔜 POST /api/admin/equipes/

Créer une équipe (brouillon).

---

### 🔜 PUT /api/admin/equipes/{id}/

Modifier une équipe.

---

### 🔜 POST /api/admin/equipes/{id}/valider/

Valider l’inscription (règles min/max, âge Rookie).

---

### 🔜 DELETE /api/admin/equipes/{id}/

Supprimer une équipe (si autorisé).

---

## 4. Phases

### 🔜 POST /api/admin/phases/

Créer une phase globale (P1 / P2 / Finale).

---

### 🔜 POST /api/admin/phases/{id}/ouvrir/

Ouvrir une phase (statut → OUVERTE).

---

### ⛔ POST /api/admin/phases/{id}/cloturer/

Clôturer une phase globale.

**Statut :** en pause
Dépend de :

* règles Phase 2
* décision admin en cas d’impair
* départages validés

---

## 5. Groupes

### ✅ GET /api/admin/groupes/

Lister les groupes d’une sous-phase.

---

### ✅ POST /api/admin/groupes/generer/

Générer automatiquement les groupes d’une sous-phase.

**Statut :** implémenté
**Contraintes :**

* min 8 équipes
* pas de groupes de 3
* cas 8/9/10/11/12+ gérés

---

### ✅ POST /api/admin/groupes/swap-equipes/

Interchanger deux équipes entre deux groupes.

**Statut :** implémenté
**Payload :**

```json
{
  "groupe_a_id": 1,
  "equipe_a_id": 10,
  "groupe_b_id": 2,
  "equipe_b_id": 14
}
```

---

## 6. Matchs

### 🔜 POST /api/admin/matchs/generer/

Générer tous les matchs d’une phase globale.

---

### 🔜 GET /api/admin/matchs/

Lister les matchs (filtres à venir).

---

## 7. Planning

### ✅ POST /api/admin/phases/{id}/planning/

Générer le planning de la phase globale.

**Statut :** implémenté
**Réponse :**

```json
{
  "matchs_planifies": 48,
  "creneaux_utilises": 6,
  "metriques": {...}
}
```

---

### 🔜 POST /api/admin/planning/pauses/

Ajouter une pause nommée (concours de shoot).

---

## 8. Feuilles de match

### ✅ POST /api/admin/matchs/{id}/feuille/

Créer ou récupérer la feuille de match.

**Statut :** implémenté
**Réponse :**

* sheet_code
* match_id

---

### 🔜 GET /api/admin/matchs/{id}/feuille/

Exporter la feuille (PDF / imprimable).

---

## 9. Scores

### ✅ POST /api/admin/matchs/{id}/score/

Saisir un score (non validé).

---

### ✅ POST /api/admin/matchs/{id}/score/valider/

Valider le score (verrouillage + recalcul classement).

---

### 🔜 POST /api/admin/matchs/{id}/forfait/

Déclarer un forfait.

**Payload possible :**

```json
{
  "type": "FORFAIT_A" | "FORFAIT_B" | "DOUBLE_FORFAIT"
}
```

---

## 10. Classements

### 🔜 GET /api/admin/groupes/{id}/classement/

Afficher le classement du groupe.

---

### 🔜 PUT /api/admin/classements/{id}/rang-manuel/

Départage manuel (égalité ≥ 3 équipes).

---

## 11. Phase 2 (en pause)

### ⛔ POST /api/admin/phases/{id}/phase2/

Générer Challenge / Consolante.

**Bloqué tant que règles non figées.**

---

## 🔒 Sécurité & principes

* Authentification : DRF
* Permissions : `IsAdminUser`
* Aucune logique métier dans les views
* Services transactionnels
* Tests systématiques

---

Si tu veux, au prochain message je peux :

* transformer ça en **fichier prêt à commit**
* générer **OpenAPI / Swagger**
* ou faire un **schéma visuel des flux API**
