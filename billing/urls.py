"""billing URL Configuration
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from rest_framework.routers import APIRootView, DefaultRouter

from hotels.urls import router as hotel_router

class ApiRootView(Def)

class DefaultRouter(DefaultRouter):
    def extend(self, router):
        self.registry.extend(router.registry)


router = DefaultRouter()
router.extend(hotel_router)

urlpatterns = [
    url(r'^rosetta/', include('rosetta.urls')),
]

urlpatterns += i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'', include('two_factor.urls', 'two_factor')),
    url(r'^', include(router.urls)),
    url(r'^hotels/', include('hotels.urls', namespace="hotels")))

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
