# referto/apps.py
from django.apps import AppConfig

class RefertoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'referto'

    def ready(self):
        import referto.signals  # 여기서 신호를 로드합니다.
