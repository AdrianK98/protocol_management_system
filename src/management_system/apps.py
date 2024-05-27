from django.apps import AppConfig


class ManagementSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'management_system'
    
    def ready(self):
        import management_system.signals
