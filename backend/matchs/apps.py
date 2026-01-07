from django.apps import AppConfig


class MatchsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "matchs"

    def ready(self) -> None:
        import matchs.signals  # noqa
