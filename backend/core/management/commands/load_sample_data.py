from __future__ import annotations

import random
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, Joueur
from planning.models import Terrain, TypeTerrain



"""Utilisation:

Générer (édition + 3 tournois + 20 équipes + 4 joueurs/équipe) :

python manage.py load_sample_data --reset


Changer les volumes :

python manage.py load_sample_data --equipes-par-tournoi 20 --joueurs-par-equipe 4 --rese
"""

PRENOMS = [
    "Alex", "Sam", "Noah", "Lina", "Mila", "Nina", "Léo", "Hugo", "Jade", "Emma",
    "Lucas", "Tom", "Eden", "Iris", "Sacha", "Zoé", "Max", "Enzo", "Liam", "Eva",
]
NOMS = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau",
    "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier",
]


class Command(BaseCommand):
    help = "Génère des données de démo (édition + 3 tournois + 20 équipes/tournoi + joueurs)."

    def add_arguments(self, parser):
        parser.add_argument("--edition-nom", type=str, default="NDB - Demo")
        parser.add_argument("--date-evenement", type=str, default="2026-06-20")
        parser.add_argument("--equipes-par-tournoi", type=int, default=20)
        parser.add_argument("--joueurs-par-equipe", type=int, default=4)
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Supprime les équipes/joueurs de l'édition de démo avant de régénérer",
        )

    @transaction.atomic
    def handle(self, *args, **options):

        # --- Superadmin de démo ---
        User = get_user_model()

        admin_username = "admin"
        admin_password = "admin"

        admin_user = User.objects.filter(username=admin_username).first()
        if not admin_user:
            try:
                # Cas standard Django
                User.objects.create_superuser(
                    username=admin_username,
                    password=admin_password,
                    email="admin@example.com",
                )
            except TypeError:
                # Si ton User custom n'a pas "username" ou impose d'autres champs,
                # fallback minimal : adapte ici selon ton modèle User.
                admin_user = User.objects.create(
                    username=admin_username,
                    email="admin@example.com",
                    is_staff=True,
                    is_superuser=True,
                )
                admin_user.set_password(admin_password)
                admin_user.save()

        self.stdout.write(self.style.SUCCESS("Superadmin OK: username=admin / password=admin"))

        edition_nom: str = options["edition_nom"]
        date_evenement = date.fromisoformat(options["date_evenement"])
        equipes_par_tournoi: int = options["equipes_par_tournoi"]
        joueurs_par_equipe: int = options["joueurs_par_equipe"]
        reset: bool = options["reset"]

        # 1) Edition (unique sur nom + date_evenement)
        edition, _ = Edition.objects.get_or_create(
            nom=edition_nom,
            defaults={"date_evenement": date_evenement},
        )

        # Si tu relances avec un autre --date-evenement mais même nom, on garde la cohérence:
        if edition.date_evenement != date_evenement:
            edition.date_evenement = date_evenement
            edition.save(update_fields=["date_evenement"])

        # 2) Tournois de l'édition (unique (edition, code))
        tournois = []
        for code, label in CodeTournoi.choices:
            tournoi, _ = Tournoi.objects.get_or_create(
                edition=edition,
                code=code,
                defaults={"libelle": label},
            )
            # si le tournoi existe mais libelle vide, on le met
            if not tournoi.libelle:
                tournoi.libelle = label
                tournoi.save(update_fields=["libelle"])
            tournois.append(tournoi)

        # 3) Reset (on supprime les équipes => cascade sur joueurs)
        if reset:
            Equipe.objects.filter(edition=edition).delete()

        created_equipes = 0
        created_joueurs = 0

        # 4) Equipes + joueurs
        for tournoi in tournois:
            existing_count = Equipe.objects.filter(edition=edition, tournoi=tournoi).count()
            to_create = max(0, equipes_par_tournoi - existing_count)

            for idx in range(to_create):
                # unique par édition sur le nom, donc on inclut le code tournoi + numéro
                nom_equipe = f"{tournoi.code} Team {existing_count + idx + 1:02d}"

                equipe = Equipe.objects.create(
                    edition=edition,
                    tournoi=tournoi,
                    nom=nom_equipe,
                    nom_club=f"Club {random.randint(1, 80):02d}",
                    # statut reste par défaut (BROUILLON)
                )
                created_equipes += 1

                joueurs = []
                for j in range(joueurs_par_equipe):
                    prenom = random.choice(PRENOMS)
                    nom = random.choice(NOMS)
                    joueurs.append(
                        Joueur(
                            equipe=equipe,
                            prenom=prenom,
                            nom=nom,
                            email=f"{prenom.lower()}.{nom.lower()}.{j+1}@example.com",
                            telephone=f"06{random.randint(10_000_000, 99_999_999)}",
                        )
                    )

                Joueur.objects.bulk_create(joueurs)
                created_joueurs += len(joueurs)

            self.stdout.write(
                self.style.SUCCESS(
                    f"{tournoi.get_code_display()}: +{to_create} équipes (total={existing_count + to_create})"
                )
            )


        # --- Terrains de démo (4 int / 4 ext) liés à l'édition ---
        terrains_specs = [
            ("Terrain Int 1", TypeTerrain.INTERIEUR, 1),
            ("Terrain Int 2", TypeTerrain.INTERIEUR, 2),
            ("Terrain Int 3", TypeTerrain.INTERIEUR, 3),
            ("Terrain Int 4", TypeTerrain.INTERIEUR, 4),
            ("Terrain Ext 1", TypeTerrain.EXTERIEUR, 5),
            ("Terrain Ext 2", TypeTerrain.EXTERIEUR, 6),
            ("Terrain Ext 3", TypeTerrain.EXTERIEUR, 7),
            ("Terrain Ext 4", TypeTerrain.EXTERIEUR, 8),
        ]

        created_terrains = 0
        updated_terrains = 0

        for nom, type_terrain, ordre in terrains_specs:
            obj, created = Terrain.objects.get_or_create(
                edition=edition,
                nom=nom,
                defaults={
                    "type_terrain": type_terrain,
                    "ordre": ordre,
                    "est_actif": True,
                },
            )

            if created:
                created_terrains += 1
            else:
                # Si déjà présent, on remet d'équerre type/ordre/actif
                changed = False
                if obj.type_terrain != type_terrain:
                    obj.type_terrain = type_terrain
                    changed = True
                if obj.ordre != ordre:
                    obj.ordre = ordre
                    changed = True
                if obj.est_actif is not True:
                    obj.est_actif = True
                    changed = True

                if changed:
                    obj.save(update_fields=["type_terrain", "ordre", "est_actif"])
                    updated_terrains += 1

        self.stdout.write(self.style.SUCCESS(f"Terrains OK: +{created_terrains} créés, {updated_terrains} mis à jour"))

        self.stdout.write(self.style.SUCCESS(f"Edition: {edition.nom} ({edition.date_evenement})"))
        self.stdout.write(self.style.SUCCESS(f"Equipes créées: {created_equipes}"))
        self.stdout.write(self.style.SUCCESS(f"Joueurs créés: {created_joueurs}"))
