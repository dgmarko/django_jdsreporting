from django.db import models
from django.urls import reverse

class Product(models.Model):
    """
    Model representing a vendors product
    """
    asin = models.CharField('ASIN',max_length=50, help_text="ASIN for the product", primary_key=True)
    product_name = models.CharField('Product Name',max_length=200, help_text="ASIN Name for the product", null=True, blank=True)
    warehouse_units = models.IntegerField(help_text='Units stored at Amazon Warehouse', null=True, blank=True)
    external_id = models.CharField(max_length=200, help_text='External ID', null=True, blank=True)
    released = models.DateField(help_text='Date Released',null=True, blank=True)
    list_price = models.FloatField(help_text='List Price',null=True, blank=True)
    product_group = models.CharField(max_length=200, help_text='Product Group', null=True, blank=True)
    category = models.CharField(max_length=100, help_text='Category', null=True, blank=True)
    sub_category = models.CharField(max_length=150, help_text='Sub Category', null=True, blank=True)
    model_number = models.CharField(max_length=150, help_text='Model Number', null=True, blank=True)
    catalog_number = models.CharField(max_length=150, help_text='Catalog Number', null=True, blank=True)
    replenishment_code = models.CharField(max_length=150, help_text='Replenishment Code', null=True, blank=True)
    page_view_rank = models.IntegerField(help_text='Page View Rank', null=True, blank=True)
    brand_code = models.CharField(max_length=50, help_text='Brand Code', null=True, blank=True)
    vendor = models.CharField(max_length=50, help_text='Vendor')

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.asin

    class Meta:
        permissions = (('can_input_data', "Able to Input Data"),)

class SalesDiagnostic(models.Model):
    """
    Model representing a sales Diagnostic entry
    """
    asin = models.CharField('ASIN',max_length=50, help_text="ASIN for the product")
    date = models.DateField(help_text='Date Released')
    asin_date  = models.CharField('ASIN_Date Combined',max_length=50, help_text="ASIN_Date Combo for the entry", primary_key=True)
    product_name = models.CharField('Product Name',max_length=200, help_text="ASIN Name for the product", null=True, blank=True)
    shipped_cogs = models.DecimalField(help_text='Shipped Cost of Goods Sold',max_digits=14, decimal_places=2,null=True, blank=True)
    shipped_cogs_perc = models.DecimalField(help_text='Shipped Cost of Goods Sold Percentage of Total',max_digits=8, decimal_places=5,null=True, blank=True)
    shipped_cogs_prior_period = models.DecimalField(help_text='Shipped Cost of Goods Sold Change From Prior Period',max_digits=14, decimal_places=2,null=True, blank=True)
    shipped_cogs_last_year = models.DecimalField(help_text='Shipped Cost of Goods Sold Change From Last Year',max_digits=8, decimal_places=5,null=True, blank=True)
    shipped_units = models.IntegerField(help_text='Shipped Units', null=True, blank=True)
    shipped_units_perc = models.DecimalField(help_text='Shipped Units Percentage of Total',max_digits=8, decimal_places=5,null=True, blank=True)
    shipped_units_prior_period = models.DecimalField(help_text='Shipped Units Change From Prior Period',max_digits=14, decimal_places=2,null=True, blank=True)
    shipped_units_last_year = models.DecimalField(help_text='Shipped Units Change From Last Year',max_digits=8, decimal_places=5,null=True, blank=True)
    customer_returns = models.IntegerField(help_text='Customer Returns', null=True, blank=True)
    free_replacements = models.IntegerField(help_text='Free Replacements', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, default="")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.asin

    class Meta:
        permissions = (('can_input_data', "Able to Input Data"),)

class InventoryHealth(models.Model):
    """
    Model representing an Inventry Health entry
    """
    asin = models.CharField('ASIN',max_length=50, help_text="ASIN for the product")
    date = models.DateField(help_text='Date Released')
    asin_date  = models.CharField('ASIN_Date Combined',max_length=50, help_text="ASIN_Date Combo for the entry", primary_key=True)
    product_name = models.CharField('Product Name',max_length=200, help_text="ASIN Name for the product", null=True, blank=True)
    net_received = models.DecimalField(help_text='Net Received Money',max_digits=14, decimal_places=2,null=True, blank=True)
    net_received_units = models.IntegerField(help_text='Net Received Units', null=True, blank=True)
    sell_through_rate = models.DecimalField(help_text='Sell-Through Rate',max_digits=8, decimal_places=5,null=True, blank=True)
    open_purchase_oq = models.IntegerField(help_text='Open Purchase Order Quantity', null=True, blank=True)
    sellable_oh_inven = models.DecimalField(help_text='Sellable On Hand Inventory',max_digits=14, decimal_places=2,null=True, blank=True)
    sellable_oh_inven_trail = models.DecimalField(help_text='Sellable On Hand Inventory - Trailing 30-day Average',max_digits=14, decimal_places=2,null=True, blank=True)
    sellable_oh_units = models.IntegerField(help_text='Sellable On Hand Units', null=True, blank=True)
    unsellable_oh_inven = models.DecimalField(help_text='Unsellable On Hand Inventory',max_digits=14, decimal_places=2,null=True, blank=True)
    unsellable_oh_inven_trail = models.DecimalField(help_text='Unsellable On Hand Inventory - Trailing 30-day Average',max_digits=14, decimal_places=2,null=True, blank=True)
    unsellable_oh_units = models.IntegerField(help_text='Unsellable On Hand Units', null=True, blank=True)
    aged_90_sellable = models.DecimalField(help_text='Aged 90+ Days Sellable Inventory',max_digits=14, decimal_places=2,null=True, blank=True)
    aged_90_sellable_trail = models.DecimalField(help_text='Aged 90+ Days Sellable Inventory - Trailing 30-day Average',max_digits=14, decimal_places=2,null=True, blank=True)
    aged_90_sellable_units = models.IntegerField(help_text='Aged 90+ Days Sellable Units', null=True, blank=True)
    repl_category = models.CharField(max_length=70, help_text="Replenishment Category")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.asin

    class Meta:
        permissions = (('can_input_data', "Able to Input Data"),)

class SponsoredProduct(models.Model):
    """
    Model representing a Sponsored Product entry
    """
    start_date = models.DateField(help_text='Start Date of Campaign')
    end_date = models.DateField(help_text='End Date of Campaign')
    currency = models.CharField(max_length=10, help_text="Currency", null=True, blank=True)
    campaign_name = models.CharField(max_length=150, help_text="Campaign Name", null=True, blank=True)
    asin = models.CharField(max_length=150, help_text="Campaign Name")
    impressions = models.IntegerField(help_text='Impressions', null=True, blank=True)
    clicks = models.IntegerField(help_text='Clicks', null=True, blank=True)
    ctr = models.DecimalField(help_text='Click-Thru Rate (CTR)',max_digits=8, decimal_places=5, null=True, blank=True)
    cpc = models.DecimalField(help_text='Cost Per Click (CPC)',max_digits=8, decimal_places=5, null=True, blank=True)
    spend = models.DecimalField(help_text='Spend',max_digits=8, decimal_places=5, null=True, blank=True)
    f_day_sales = models.DecimalField(help_text='Spend',max_digits=11, decimal_places=2, null=True, blank=True)
    acos = models.DecimalField(help_text='Total Advertising Cost of Sales (ACoS)',max_digits=8, decimal_places=5, null=True, blank=True)
    raos = models.DecimalField(help_text='Total Return on Advertising Spend (RoAS)',max_digits=8, decimal_places=2, null=True, blank=True)
    f_day_orders = models.IntegerField(help_text='14 Day Total Orders (#)', null=True, blank=True)
    f_day_units = models.IntegerField(help_text='14 Day Total Units (#)', null=True, blank=True)
    f_day_conv_rate = models.DecimalField(help_text='14 Day Conversion Rate',max_digits=8, decimal_places=2, null=True, blank=True)
    campasin = models.CharField(max_length=150, help_text="Campaign Name ASIN Combo", primary_key=True)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.campasin

    class Meta:
        permissions = (('can_input_data', "Able to Input Data"),)

class InventoryForecast(models.Model):
    """
    Model representing a Sponsored Product entry
    """
    asin = models.CharField('ASIN',max_length=50, help_text="ASIN for the product")
    date = models.DateField(help_text='Date Released')
    asin_date  = models.CharField('ASIN_Date Combined',max_length=50, help_text="ASIN_Date Combo for the entry", primary_key=True)
    week_forecast = models.IntegerField(help_text='Weekly Inventory Forecast', null=True, blank=True)
    week2_forecast = models.IntegerField(help_text='Next Weeks Inventory Forecast', null=True, blank=True)
    week3_forecast = models.IntegerField(help_text='3 Weeks Out Inventory Forecast', null=True, blank=True)
    week4_forecast = models.IntegerField(help_text='4 Weeks Out Inventory Forecast', null=True, blank=True)
    week5_forecast = models.IntegerField(help_text='5 Weeks Out Inventory Forecast', null=True, blank=True)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.asin

    class Meta:
        permissions = (('can_input_data', "Able to Input Data"),)

class Headers(models.Model):
    """
    Model representing the header dictionary
    """
    amazon_header = models.CharField('Amazon Header', max_length=200, help_text='Amazon CSV Header', primary_key=True)
    database_header = models.CharField('Database Header', max_length=200, help_text='Database Header')

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.amazon_header

    class Meta:
        permissions = (('can_add_new_headers', "Able to Amend Amazon Database Headers"),)

class Checks(models.Model):
    """
    Model representing the checks dictionary
    """
    amazon_header = models.CharField('Amazon Header', max_length=200, help_text='Amazon CSV Header', primary_key=True)
    file_type = models.CharField('File Type', max_length=200, help_text='File')

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.amazon_header

    class Meta:
        permissions = (('can_add_new_checks', "Able to Amend Amazon Database Checks"),)

class VendorASIN(models.Model):
    """
    Model representing ASIN checks to determine vendor
    """
    asin = models.CharField('ASIN',max_length=50, help_text="ASIN for the product", primary_key=True)
    vendor = models.CharField('Vendor',max_length=50, help_text="Vendor for the ASIN")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.asin

    class Meta:
        permissions = (('can_add_new_vendors', "Able to add Vendor ASIN Checks"),)
