from django.apps import AppConfig


class EventsConfig(AppConfig):
    """
    Application configuration for the Events app.

    Defines application metadata and ensures that signal
    handlers are registered when Django initializes the app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.events"
    verbose_name = "Events"

    def ready(self):
        """
        Import signal handlers at application startup.

        This guarantees that all model lifecycle hooks
        (post_save, post_delete, etc.) are properly registered.
        """
        import apps.events.signals  # noqa: F401