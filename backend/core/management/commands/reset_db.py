from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = "Reset la DB SQLite (supprime db.sqlite3), relance migrate."

    def add_arguments(self, parser):
        parser.add_argument(
            "--seed",
            action="store_true",
            help="Lance aussi le seed MVP après reset (nécessite une commande seed_mvp).",
        )

    def handle(self, *args, **options):
        db_path = Path(settings.DATABASES["default"]["NAME"])

        if db_path.exists():
            db_path.unlink()
            self.stdout.write(self.style.SUCCESS(f"Supprimé: {db_path}"))
        else:
            self.stdout.write(f"Aucun fichier DB à supprimer: {db_path}")

        call_command("migrate", interactive=False)
        self.stdout.write(self.style.SUCCESS("DB reset + migrate terminé."))

        if options.get("--seed") or options.get("seed"):
            call_command("seed_mvp")
            self.stdout.write(self.style.SUCCESS("Seed MVP terminé."))
