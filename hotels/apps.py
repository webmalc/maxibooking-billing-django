from django.apps import AppConfig


class HotelsConfig(AppConfig):
    name = 'hotels'

    def ready(self):
        import hotels.signals
