from import_export import resources
from .models import Product, SalesDiagnostic, InventoryHealth, SponsoredProduct, InventoryForecast

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        import_id_fields = ['asin']

class SalesDiagnosticResource(resources.ModelResource):
    class Meta:
        model = SalesDiagnostic
        import_id_fields = ['asin_date']

class InventoryHealthResource(resources.ModelResource):
    class Meta:
        model = InventoryHealth
        import_id_fields = ['asin_date']

class SponsoredProductResource(resources.ModelResource):
    class Meta:
        model = SponsoredProduct
        import_id_fields = ['campasin']

class InventoryForecastResource(resources.ModelResource):
    class Meta:
        model = InventoryForecast
        import_id_fields = ['asin_date']
