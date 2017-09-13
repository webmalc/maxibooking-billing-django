from django.apps import AppConfig


class FinancesConfig(AppConfig):
    name = 'finances'

    def ready(self):
        import finances.signals
