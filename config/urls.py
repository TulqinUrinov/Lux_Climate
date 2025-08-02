from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions


class JWTchemaGenerator(OpenAPISchemaGenerator):
    def get_security_definitions(self):
        return {
            "Bearer": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Format: Bearer <access_token>",
            }
        }


schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version="v1",
        description="Lux Climate API",
        contact=openapi.Contact(email="tulqinurinov005@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    generator_class=JWTchemaGenerator,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("data.bot.urls")),
    path("api/", include("data.user.urls")),
    path("api/customers/", include("data.customer.urls")),
    path("api/orders/", include("data.order.urls")),
    path("api/", include("data.balance.urls")),
    path("api/", include("data.file.urls")),
    path("api/payments/", include("data.payment.urls")),
    # Swagger
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
