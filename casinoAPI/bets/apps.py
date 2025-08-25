from django.apps import AppConfig


class BetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bets'

    def ready(self):
        try:
            from .tasks import start_settlement_scheduler
            start_settlement_scheduler()
        except Exception:
            # 避免迁移等阶段导入失败影响启动
            pass
