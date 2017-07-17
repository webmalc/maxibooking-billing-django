from rest_framework.routers import DefaultRouter


class DefaultRouter(DefaultRouter):
    def extend(self, router):
        self.registry.extend(router.registry)
