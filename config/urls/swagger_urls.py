from django.conf.urls import url
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


"""
https://github.com/axnsan12/drf-yasg

This exposes 4 endpoints:

A JSON view of your API specification at /swagger.json
A YAML view of your API specification at /swagger.yaml
A swagger-ui view of your API specification at /swagger/
A ReDoc view of your API specification at /redoc/
"""


schema_view = get_schema_view(
    openapi.Info(
        title="Fullfii API",
        default_version="v4",
        description="",
        terms_of_service="http://192.168.11.46:8080/terms-of-service/",
        contact=openapi.Contact(email="fullfii811@gmail.com"),
        license=openapi.License(name="fullfii"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    url(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    url(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
