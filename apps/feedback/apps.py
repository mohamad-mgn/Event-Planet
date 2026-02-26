from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    """
    Application configuration for the Feedback app.

    Defines the default primary key type, application name,
    human-readable verbose name, and ensures signal registration
    when the application is fully loaded.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.feedback'
    verbose_name = 'Feedback'

    def ready(self):
        """
        Import signal handlers when the application is ready.

        Ensures that all model signals defined in the app
        are properly registered at startup.
        """
        import apps.feedback.signals