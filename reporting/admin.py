from django.contrib import admin

from .models import Product, Headers, Checks, VendorASIN

admin.site.register(Product)
admin.site.register(Headers)
admin.site.register(Checks)
admin.site.register(VendorASIN)
