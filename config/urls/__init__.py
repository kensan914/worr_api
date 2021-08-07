from django.contrib import admin
from django.urls import path, include
from config import settings
from config.urls import swagger_urls


urlpatterns = [
    # path("api/v1/", include("api.urls")),
    # path('api/v2/', include('api.v2.urls')),
    # path('api/v3/', include('api.v3.urls')),
    path("api/v4/", include("api.v4.urls")),
    path("", include("main.urls")),
    # HACK:
    path("maintenance-mode/", include("maintenance_mode.urls")),
]

if settings.ADMIN:
    admin.site.site_header = "Fullfii 管理サイト"
    admin.site.site_title = "Fullfii 管理サイト"
    admin.site.index_title = "HOME🏠"
    urlpatterns += [path("admin/", admin.site.urls)]


# only Debugging
if settings.DEBUG:
    urlpatterns += [
        path("", include(swagger_urls)),
    ]
