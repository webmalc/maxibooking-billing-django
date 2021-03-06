"""billing URL Configuration
"""
from ajax_select import urls as ajax_select_urls
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView
from rest_framework_swagger.views import get_swagger_view
from two_factor.urls import urlpatterns as two_factor_urls

from clients.urls import router as clients_router
from finances.urls import router as finances_router
from fms.urls import router as fms_router
from hotels.urls import router as hotels_router

from .routers import DefaultRouter

router = DefaultRouter()
router.extend(hotels_router, clients_router, finances_router, fms_router)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^rosetta/', include('rosetta.urls')),
    url(r'', include(two_factor_urls)),
]

schema_view = get_swagger_view(title='Billing API')

urlpatterns += i18n_patterns(
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^swagger/', schema_view),
    url(r'^adminactions/', include('adminactions.urls')),
    url(r'^finances/',
        include(('finances.urls', 'finances'), namespace='finances')),
    url(r'^billing/processing$',
        xframe_options_exempt(
            TemplateView.as_view(template_name='billing/processing.html')),
        name='billing-processing'),
    url(r'^billing/payment-successful$',
        xframe_options_exempt(
            TemplateView.as_view(
                template_name='billing/payment_successful.html')),
        name='billing-payment-successful'),
    url(r'^billing/fail$',
        xframe_options_exempt(
            TemplateView.as_view(template_name='billing/fail.html')),
        name='billing-fail'),
    url(r'^', include(router.urls)),
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
