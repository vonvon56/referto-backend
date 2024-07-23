from django.apps import AppConfig


class PapersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'papers'
    
    def ready(self):
        import papers.signals  # 신호 등록

