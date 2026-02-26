from django.apps import AppConfig

class RegistrationsConfig(AppConfig):
    """
    Configuration for the Registrations app.

    Sets default primary key type and verbose name, and ensures
    signals are imported when the app is ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.registrations'
    verbose_name = 'Registrations'

    def ready(self):
        """
        Import app signals when the application is fully loaded.

        This ensures that signal handlers are registered and ready
        to handle events such as model save or delete actions.
        """
        import apps.registrations.signals
