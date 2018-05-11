from django import forms
from .models import SalesDiagnostic, Product, Headers
from django.contrib.auth.models import User


class ReportForm(forms.Form):
    choices = Product.objects.values("vendor")
    VENDOR_OPTIONS = ()
    for i in choices:
        choice = (i['vendor'], i['vendor'])
        if choice not in VENDOR_OPTIONS:
            VENDOR_OPTIONS += (choice),

    headData = Headers.objects.values()
    OPTIONS = ()
    for i in headData:
        choice = (i['database_header'], i['amazon_header'])
        if i['database_header'] != 'asin':
            OPTIONS += (choice),

    vendor = forms.ChoiceField(choices=VENDOR_OPTIONS)
    report_date = forms.DateField(widget=forms.DateInput)
    headers = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=OPTIONS)

    def return_vend(self):
        self.vendor()

    def __init__(self, user, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.user = user
        # assign a (computed, I assume) default value to the choice field
        self.initial['headers'] = ['model_number', 'asin_name', 'shipped_cogs', 'shipped_units', 'sellable_oh_inven',
        'aged_90_sellable', 'repl_category', 'impressions', 'clicks', 'ctr', 'cpc', 'spend', 'f_day_sales',
        'f_day_orders', 'f_day_units', 'week_forecast']
