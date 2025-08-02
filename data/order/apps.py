from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data.order"

    def ready(self):

        import data.order.signals
