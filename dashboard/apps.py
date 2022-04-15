from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'


    # Override default signals to allow Profile creation
    def ready(self):
        import dashboard.signals


