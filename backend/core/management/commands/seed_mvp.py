from __future__ import annotations

from datetime import date
from typing import Iterable

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, Joueur, StatutEquipe
from phases.models import PhaseGlobale, TypePhaseGlobale
from phases.models import SousPhase  # pour itérer après génération sous-phases

from planning.models import Terrain, TypeTerrain  # adapte si ton TypeTerrain est ailleurs

from phases.services.sous_phases import generer_sous_phases_pour_phase_globale
from groupes.services_phase1 import (
    generer_groupes_phase1_pour_sous_phase,
    ErreurGenerationGroupes,
)
from matchs.services_generation import generer_matchs_pour_phase_globale
from planning.services_planning import generer_planning_phase_globale


def _mk_admin(username: str, email: str, password: str):
    User = get_user_model()
    u = User.objects.filter(username=username).first()
    if u:
        return u

    # Django superuser standard
    return User.objects.create_superuser(username=username, email=email, password=password)


def _mk_terrains(edition: Edition, nb: int = 8):
    if Terrain.objects.filter(edition=edition).exists():
        return

    terrains = []
    for i in range(1, nb + 1):
        terrains.append(
            Terrain(
                edition=edition,
                nom=f"T{i}",
                # adapte selon tes choix: INTERIEUR/EXTERIEUR etc.
                type_terrain=getattr(TypeTerrain, "INTERIEUR", "INTERIEUR"),
                ordre=i,
                est_actif=True,
            )
        )
    Terrain.objects.bulk_create(terrains)


def _mk_equipes(edition: Edition, tournoi: Tournoi, n: int, start_index: int = 1) -> list[Equipe]:
    created = []
    for i in range(start_index, start_index + n):
        equipe, _ = Equipe.objects.get_or_create(
            edition=edition,
            tournoi=tournoi,
            nom=f"{tournoi.code}-E{i:02d}",
            defaults={
                "statut": StatutEquipe.VALIDEE,
                "nom_club": f"Club {tournoi.code}",
            },
        )
        # Force le statut si existait en BROUILLON
        if equipe.statut != StatutEquipe.VALIDEE:
            equipe.statut = StatutEquipe.VALIDEE
            equipe.save(update_fields=["statut"])

        created.append(equipe)
    return created


def _mk_joueurs(equipe: Equipe, n: int = 4):
    if equipe.joueurs.exists():
        return
    Joueur.objects.bulk_create(
        [
            Joueur(
                equipe=equipe,
                prenom=f"J{i}",
                nom=f"{equipe.nom}",
                email="",
                telephone="",
            )
            for i in range(1, n + 1)
        ]
    )


class Command(BaseCommand):
    help = "Seed MVP: édition + admin + tournois + équipes/joueurs + phase1 + groupes + matchs + planning."

    def add_arguments(self, parser):
        parser.add_argument("--edition-nom", default="NDB 2026", type=str)
        parser.add_argument("--edition-date", default="2026-06-20", type=str)
        parser.add_argument("--equipes-par-tournoi", default=10, type=int)
        parser.add_argument("--admin-user", default="admin", type=str)
        parser.add_argument("--admin-email", default="admin@example.com", type=str)
        parser.add_argument("--admin-pass", default="admin123", type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        edition_nom = options["edition_nom"]
        edition_date = date.fromisoformat(options["edition_date"])
        n_equipes = int(options["equipes_par_tournoi"])

        admin_user = options["admin_user"]
        admin_email = options["admin_email"]
        admin_pass = options["admin_pass"]

        # 1) Admin
        admin = _mk_admin(admin_user, admin_email, admin_pass)
        self.stdout.write(self.style.SUCCESS(f"Admin OK: {admin.username} / {admin_email}"))

        # 2) Edition
        edition, _ = Edition.objects.get_or_create(
            nom=edition_nom,
            defaults={"date_evenement": edition_date},
        )
        if edition.date_evenement != edition_date:
            edition.date_evenement = edition_date
            edition.save(update_fields=["date_evenement"])
        self.stdout.write(self.style.SUCCESS(f"Edition OK: {edition.id} {edition.nom}"))

        # 3) Terrains
        _mk_terrains(edition, nb=8)
        self.stdout.write(self.style.SUCCESS("Terrains OK"))

        # 4) Tournois
        tournois = []
        for code in (CodeTournoi.ROOKIE, CodeTournoi.LOISIR, CodeTournoi.COMPETITEUR):
            t, _ = Tournoi.objects.get_or_create(
                edition=edition,
                code=code,
                defaults={"libelle": code.label if hasattr(code, "label") else ""},
            )
            tournois.append(t)
        self.stdout.write(self.style.SUCCESS("Tournois OK"))

        # 5) Equipes + joueurs
        for t in tournois:
            equipes = _mk_equipes(edition, t, n=n_equipes, start_index=1)
            for e in equipes:
                _mk_joueurs(e, n=4)
        self.stdout.write(self.style.SUCCESS("Equipes + joueurs OK"))

        # 6) Phase 1
        phase1, _ = PhaseGlobale.objects.get_or_create(
            edition=edition,
            type_phase=TypePhaseGlobale.PHASE_1,
            defaults={"sequence": 1},
        )
        self.stdout.write(self.style.SUCCESS(f"Phase 1 OK: {phase1.id}"))

        # 7) Sous-phases phase 1
        generer_sous_phases_pour_phase_globale(phase1)
        self.stdout.write(self.style.SUCCESS("Sous-phases phase 1 OK"))

        # 8) Groupes phase 1 (par sous-phase)
        sous_phases = SousPhase.objects.filter(phase_globale=phase1).select_related("tournoi")
        for sp in sous_phases:
            generer_groupes_phase1_pour_sous_phase(sp)
        self.stdout.write(self.style.SUCCESS("Groupes phase 1 OK"))

        # 9) Matchs phase 1
        generer_matchs_pour_phase_globale(phase1)
        self.stdout.write(self.style.SUCCESS("Matchs phase 1 OK"))

        # 10) Planning phase 1
        generer_planning_phase_globale(phase1)
        self.stdout.write(self.style.SUCCESS("Planning phase 1 OK"))

        self.stdout.write(self.style.SUCCESS("Seed MVP terminé."))
