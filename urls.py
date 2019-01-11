from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

# from django.conf import settings

urlpatterns = [
    # Example:
    url(r'^', include('halolib.halolib.urls')),
    # url(r'^(?P<url>.*)$', proxy),#, ProxyLink.as_view(), name='proxy'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # url(r'^api-token-auth/', include('rest_framework.authtoken.views.obtain_auth_token')),
]  # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
