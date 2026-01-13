from __future__ import annotations

import random
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Edition
from tournois.models import Tournoi, CodeTournoi
from inscriptions.models import Equipe, Joueur


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

        self.stdout.write(self.style.SUCCESS(f"Edition: {edition.nom} ({edition.date_evenement})"))
        self.stdout.write(self.style.SUCCESS(f"Equipes créées: {created_equipes}"))
        self.stdout.write(self.style.SUCCESS(f"Joueurs créés: {created_joueurs}"))
