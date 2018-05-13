from django.shortcuts import render
from django.utils.http import is_safe_url
from django.shortcuts import redirect
from django.db.models import Sum, Q
from .models import Product, Headers, Checks, VendorASIN, SalesDiagnostic, InventoryHealth, SponsoredProduct, InventoryForecast
from .resources import ProductResource, SalesDiagnosticResource, InventoryHealthResource, SponsoredProductResource, InventoryForecastResource
from .forms import ReportForm
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Permission, User
from django.views import View
from django.views.generic.edit import FormView
import django_tables2 as tables
from django_tables2 import RequestConfig
from tablib import Dataset
from datetime import datetime, timedelta
import re
import json
from decimal import Decimal
import psycopg2
from django.db import transaction, DatabaseError
from django.db.transaction import atomic

def get_user_permissions(user):
    if user.is_superuser:
        return Permission.objects.all()
    return user.user_permissions.all() | Permission.objects.filter(group__user=user)

def verifyInput(inFile, ftype):
    dictCheck = {}
    check = Checks.objects.all()
    for j in check:
        if j.file_type == ftype:
            dictCheck[j.amazon_header] = j.file_type
    checkCount = 0
    if ftype == 'spon_prod':
        for i in inFile.headers:
            if i in dictCheck:
                checkCount += 1
    elif ftype == 'sales_diag' or ftype == 'inv_health' or ftype == 'inv_fore' or ftype == 'prod_table':
        firstLine = True
        for i in inFile:
            if firstLine:
                headers = list(i)
            firstLine = False
        for i in headers:
            if i in dictCheck:
                checkCount += 1
    print(checkCount)
    if checkCount >= 3:
        return True
    else:
        return False

def findVendor(inFile):
    dictCheck = {}
    dataR = []
    check = VendorASIN.objects.all()
    vendCount = 0
    for j in check:
        dictCheck[j.asin] = j.vendor
    for i in inFile:
        dataR = list(i)
        for j in dataR:
            if j in dictCheck and vendCount == 0:
                vendor = dictCheck[j]
                vendCount += 1
            elif j in dictCheck:
                if dictCheck[j] == vendor:
                    vendCount +=1
    if vendCount >= 3:
        print('Success')
        return vendor
    else:
        print('Failure')
        return 'Fail'



def convertInput(inFile, ftype):
    headList = []
    dictHead = {}
    outSet = Dataset()
    #Pull header mapping from database
    modelHead = Headers.objects.all()
    for j in modelHead:
        dictHead[j.amazon_header] = j.database_header
    #regex to find csv date formats for conversion
    p = re.compile('^\d{4}[\-\/\s]?((((0[13578])|(1[02]))[\-\/\s]?(([0-2][0-9])|(3[01])))|(((0[469])|(11))[\-\/\s]?(([0-2][0-9])|(30)))|(02[\-\/\s]?[0-2][0-9]))$')
    q = re.compile('(0?[1-9]|1[012])\/(0?[1-9]|[12][0-9]|3[01])\/\d{4}')
    sp = re.compile('^(?:(((Jan(uary)?|Ma(r(ch)?|y)|Jul(y)?|Aug(ust)?|Oct(ober)?|Dec(ember)?)\ 31)|((Jan(uary)?|Ma(r(ch)?|y)|Apr(il)?|Ju((ly?)|(ne?))|Aug(ust)?|Oct(ober)?|(Sept|Nov|Dec)(ember)?)\ (0?[1-9]|([12]\d)|30))|(Feb(ruary)?\ (0?[1-9]|1\d|2[0-8]|(29(?=,\ ((1[6-9]|[2-9]\d)(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00)))))))\,\ ((1[6-9]|[2-9]\d)\d{2}))')
    dregex = re.compile('\d+(\.\d{1,2})?')
    #if file import product table
    if ftype == 'prod_table':
        vendor = findVendor(inFile)

        if vendor != 'Fail':
            headFirst = False

            for i in inFile.headers:
                if i == 'ASIN':
                    headFirst = True

            headers = []

            if not headFirst:
                dictH = {'asin':-1, 'product_name':-1, 'warehouse_units':-1, 'external_id':-1, 'released':-1, 'list_price':-1,
                'product_group':-1, 'category':-1, 'sub_category':-1, 'model_number':-1, 'catalog_number':-1, 'replenishment_code':-1,
                'page_view_rank':-1, 'brand_code':-1}

                firstLine = True
                for i in inFile:
                    if firstLine:
                        headVal = list(i)
                    firstLine = False

                count = 0

                for i in headVal:
                    if i in dictHead:
                        if dictHead[i] in dictH:
                            dictH[dictHead[i]] = count
                    count += 1

            for i in dictH:
                headList.append(i)

            headList.append('vendor')
            outSet.headers = headList
            firstLine = True

            for i in inFile:
                if not firstLine:
                    outList = []
                    dat = list(i)
                    for j in dictH:
                        if dictH[j] != -1:
                            val = dat[dictH[j]]
                            if p.match(val):
                                try:
                                    val = datetime.strptime(val, '%Y/%m/%d')
                                except:
                                    pass
                                try:
                                    val = datetime.strptime(val, '%Y-%m-%d')
                                except:
                                    pass
                                outList.append(val)
                            elif q.match(val):
                                val = datetime.strptime(val, '%m/%d/%Y')
                                outList.append(val)
                            else:
                                if '$' in val:
                                    val = val.replace('$', '')
                                if ',' in val:
                                    val = val.replace(',', '')
                                outList.append(val)
                        else:
                            outList.append(None)

                    outList.append(vendor)
                    outSet.append(tuple(outList))
                firstLine = False
            return outSet
        else:
            #Code here for no vendor match
            return inFile
    elif ftype == 'spon_prod':
        for i in inFile.headers:
            if i in dictHead:
                headList.append(dictHead[i])
            else:
                headList.append(i)

        headList.append('campasin')
        outSet.headers = headList

        for i in inFile:
            outList = []
            dat = list(i)
            for j in dat:
                if p.match(j):
                    j = datetime.strptime(j, '%Y/%m/%d')
                elif q.match(j):
                    j = datetime.strptime(j, '%m/%d/%Y')
                elif sp.match(j):
                    j = datetime.strptime(j, '%b %d, %Y')
                elif '%' in j:
                    j = round(float(j[0:len(j)-1]) / 100, 2)
                elif '$' in j:
                    if ',' in j:
                        j = j.replace(',', '')
                    j = float(j[1:])
                elif j == '—':
                    j = 0
                elif dregex.match(j):
                    if ',' in j:
                        j = j.replace(',', '')
                    j = float(j)

                outList.append(j)
            outList.append(dat[3] + dat[4])
            outSet.append(tuple(outList))

        return outSet
    elif ftype == 'sales_diag':
        #Code to convert Sales Diagnostic csv into dataset taht can be pushed to db
        #Find date of the File
        for i in inFile.headers:
            if 'Viewing=[' in i:
                dateStr = i[9:].split("-")
                if '/' in dateStr[0]:
                    if ' ' in dateStr[0]:
                        dateStr[0].replace(' ', '')
                    dateOut = dateStr[0]
                else:
                    dateOut = dateStr[0][:4] + "/" + dateStr[0][4:6] + "/" + dateStr[0][6:]

        dictH = {'asin':-1, 'date':-1, 'asin_date':-1, 'product_name':-1, 'shipped_cogs':-1, 'shipped_cogs_perc':-1,
        'shipped_cogs_prior_period':-1, 'shipped_cogs_last_year':-1, 'shipped_units':-1, 'shipped_units_perc':-1, 'shipped_units_prior_period':-1,
        'shipped_units_last_year':-1, 'customer_returns':-1, 'free_replacements':-1}

        headers = []

        #Move to the next line and create the headers list
        firstLine = True
        for i in inFile:
            if firstLine:
                headVal = list(i)
            firstLine = False

        count = 0

        for i in headVal:
            if i in dictHead:
                if dictHead[i] in dictH:
                    dictH[dictHead[i]] = count
            count += 1

        print(dictH)

        for i in dictH:
            headers.append(i)

        headers.append('product')

        outSet.headers = headers
        firstLine = True
        #Iterate through data making necessary conversions and tying data instances to product
        for i in inFile:
            if not firstLine:
                outList = []
                dat = list(i)
                for j in dictH:
                    if dictH[j] != -1:
                        val = dat[dictH[j]]
                        if p.match(val):
                            try:
                                val = datetime.strptime(val, '%Y/%m/%d')
                            except:
                                pass
                            try:
                                val = datetime.strptime(val, '%Y-%m-%d')
                            except:
                                pass
                        elif q.match(val):
                            try:
                                val = datetime.strptime(val, '%m/%d/%Y')
                            except:
                                pass
                            try:
                                val = datetime.strptime(val, '%m-%d-%Y')
                            except:
                                pass
                        elif '%' in val and j != 'product_name':
                            val = round(float(val[0:len(val)-1]) / 100, 2)
                        elif '$' in val and j != 'product_name':
                            if ',' in val:
                                val = val.replace(',', '')
                            val = float(val[1:])
                        elif '—' in val and j != 'product_name':
                            val = 0
                        elif dregex.match(val) and j != 'product_name':
                            if ',' in j:
                                val = val.replace(',', '')
                            val = float(val)

                        if val == '':
                            val = 0
                        outList.append(val)
                    else:
                        if j == 'date':
                            dateD = dateOut.split('/')
                            if len(dateD[0]) == 1:
                                mon = '0' + dateD[0]
                            else:
                                mon = dateD[0]

                            if len(dateD[1]) == 1:
                                da = '0' + dateD[1]
                            else:
                                da = dateD[1]

                            dateConv = mon + '/' + da + '/' + dateD[2]
                            dateConv = dateOut.replace(' ', '')

                            try:
                                outList.append(datetime.strptime(dateConv, '%Y/%m/%d'))
                            except:
                                pass
                            try:
                                outList.append(datetime.strptime(dateConv, '%m/%d/%y'))
                            except:
                                pass
                        elif j == 'asin_date':
                            outList.append(dat[0] + str(dateOut))
                        else:
                            outList.append(None)

                outList.append(Product.objects.get(pk=dat[0]))
                outSet.append(tuple(outList))
            firstLine = False

        return outSet

    elif ftype == 'inv_health':
        #Code to convert Inventory Health csv into dataset that can be pushed to db
        #Find date of the File
        for i in inFile.headers:
            if 'Viewing=[' in i:
                dateStr = i[9:].split("-")
                dateOut = dateStr[0][:4] + "/" + dateStr[0][4:6] + "/" + dateStr[0][6:]
        headers = []
        headers.append('asin')
        headers.append('date')
        headers.append('asin_date')
        #Move to the next line and create the headers list
        firstLine = True
        for i in inFile:
            if firstLine:
                headVal = list(i)
            firstLine = False
        for i in headVal:
            headers.append(i)
        headers.remove('ASIN')
        for i in headers:
            if i in dictHead:
                headList.append(dictHead[i])
            else:
                headList.append(i)
        headList.append('product')
        outSet.headers = headList
        firstLine = True

        #Iterate through data making necessary conversions and tying data instances to product
        for i in inFile:
            if not firstLine:
                for k in range(7, 14):
                    outList = []
                    dat = list(i)
                    count = 0
                    dateInv = datetime.strptime(dateOut, '%Y/%m/%d') + timedelta(days=k)
                    for j in dat:
                        if count == 0:
                            outList.append(j)
                            outList.append(dateInv)
                            outList.append(j + str(dateInv))
                        else:
                            if p.match(j):
                                j = datetime.strptime(j, '%Y/%m/%d')
                            elif q.match(j):
                                j = datetime.strptime(j, '%m/%d/%Y')
                            elif '%' in j:
                                j = round(float(j[0:len(j)-1]) / 100, 2)
                            elif '$' in j:
                                if ',' in j:
                                    j = j.replace(',', '')
                                j = float(j[1:])
                            elif j == '—':
                                j = 0
                            elif dregex.match(j):
                                if ',' in j:
                                    j = j.replace(',', '')
                                j = float(j)

                            outList.append(j)
                        count += 1

                    #map data to prdouct using asin as key
                    outList.append(Product.objects.get(pk=dat[0]))
                    outSet.append(tuple(outList))
            firstLine = False

        return outSet
    elif ftype == 'inv_fore':
        #Code to convert Inventory Forecast csv into dataset that can be pushed to db
        #Find date of the File
        for i in inFile.headers:
            if 'Viewing=[' in i:
                dateStr = i[9:].split("-")
                dateOut = dateStr[0][:4] + "/" + dateStr[0][4:6] + "/" + dateStr[0][6:]
        headers = []

        headers.append('asin')
        headers.append('date')
        headers.append('asin_date')
        headers.append('week_forecast')
        headers.append('week2_forecast')
        headers.append('week3_forecast')
        headers.append('week4_forecast')
        headers.append('week5_forecast')
        #Move to the next line and create the headers list
        firstLine = True
        for i in inFile:
            if firstLine:
                headVal = list(i)
            firstLine = False
        count = 0
        for i in headVal:
            if i in dictHead:
                if dictHead[i] == 'asin':
                    asinCol = count
                elif dictHead[i] == 'week_forecast':
                    weekCol = count
                elif dictHead[i] == 'week2_forecast':
                    week2Col = count
                elif dictHead[i] == 'week3_forecast':
                    week3Col = count
                elif dictHead[i] == 'week4_forecast':
                    week4Col = count
                elif dictHead[i] == 'week5_forecast':
                    week5Col = count

            count += 1

        outSet.headers = headers
        firstLine = True

        #Iterate through data making necessary conversions and tying data instances to product
        for i in inFile:
            if not firstLine:
                for k in range(13, 14):
                    outList = []
                    dat = list(i)
                    count = 0
                    dateInv = datetime.strptime(dateOut, '%Y/%m/%d') + timedelta(days=k)

                    outList.append(dat[asinCol])
                    outList.append(dateInv)
                    outList.append(dat[asinCol]+str(dateInv))

                    if ',' in dat[weekCol]:
                        dat[weekCol] = dat[weekCol].replace(',', '')
                    outList.append(dat[weekCol])

                    if ',' in dat[week2Col]:
                        dat[week2Col] = dat[week2Col].replace(',', '')
                    outList.append(dat[week2Col])

                    if ',' in dat[week3Col]:
                        dat[week3Col] = dat[week3Col].replace(',', '')
                    outList.append(dat[week3Col])

                    if ',' in dat[week4Col]:
                        dat[week4Col] = dat[week4Col].replace(',', '')
                    outList.append(dat[week4Col])

                    if ',' in dat[week5Col]:
                        dat[week5Col] = dat[week5Col].replace(',', '')
                    outList.append(dat[week5Col])

                    print(outList)
                    outSet.append(tuple(outList))
                    print(tuple(outList))
            firstLine = False

        return outSet


class DataTable(tables.Table):
    paginate_by = 25

def create_data_output(repVendor, entry_date, heads):
    prods = Product.objects.filter(vendor=repVendor).values()
    sales = SalesDiagnostic.objects.filter(date=entry_date).values()
    invheal = InventoryHealth.objects.filter(date=entry_date).values()
    sponprod = SponsoredProduct.objects.filter(end_date__lte=entry_date).values()
    invfore = InventoryForecast.objects.filter(date=entry_date).values()
    #sponprod = SponsoredProduct.objects.all().values()start_date__gte=entry_date,
    headerNames = Headers.objects.values()
    outTable = []

    emptySale = {'asin': '', 'date': entry_date, 'asin_date':entry_date, 'product_name': '', 'shipped_cogs': None, 'shipped_cogs_perc':0,
    'shipped_cogs_perc':0, 'shipped_cogs_prior_period':0, 'shipped_cogs_last_year':0, 'shipped_units':0,
    'shipped_units_perc':0, 'shipped_units_prior_period':0, 'shipped_units_last_year':0, 'customer_returns':0,
    'free_replacements':0, 'product':''}

    emptyIH = {'asin': '', 'date': entry_date, 'asin_date':entry_date, 'product_name': '', 'net_received':0, 'net_received_units':0,
    'sell_through_rate':0, 'open_purchase_oq':0, 'sellable_oh_inven':0, 'sellable_oh_inven_trail':0,
    'sellable_oh_units':0, 'unsellable_oh_inven':0, 'unsellable_oh_inven_trail':0, 'unsellable_oh_units':0, 'aged_90_sellable':0, 'aged_90_sellable_trail':0,
    'aged_90_sellable_units':0, 'repl_category':''}

    emptySp = {'start_date': entry_date, 'end_date': entry_date, 'currency':'', 'campaign_name': '', 'asin':'', 'impressions':0,
    'clicks':0, 'ctr':0, 'cpc':0, 'spend':0, 'f_day_sales':0, 'acos':0, 'raos':0, 'f_day_orders':0, 'f_day_units':0,
    'f_day_conv_rate':0, 'campasin':''}

    emptyFore = {'asin': '', 'date': entry_date, 'asin_date':entry_date, 'week_forecast': 0, 'week2_forecast':0, 'week3_forecast':0,
    'week4_forecast':0, 'week5_forecast':0}

    heads = ['asin'] + heads

    for i in prods:
        #match sales data to each product, if no match populate empty values
        matchFound = False
        for j in sales:
            if i['asin'] == j['asin']:
                i.update(j)
                matchFound = True

        if not matchFound:
            empSale = emptySale
            empSale['asin'] = i['asin']
            i.update(empSale)

        #match inventory health data to each product, if no match populate empty values
        matchFound = False
        for j in invheal:
            if i['asin'] == j['asin']:
                i.update(j)
                matchFound = True

        if not matchFound:
            empIH = emptyIH
            empIH['asin'] = i['asin']
            i.update(empIH)

        #match sponsored product data to each product, if no match populate empty values
        matchFound = False
        for j in sponprod:
            if i['asin'] == j['asin']:
                i.update(j)
                matchFound = True

        if not matchFound:
            empIH = emptySp
            empIH['asin'] = i['asin']
            i.update(empIH)

        #match inventory forecast data to each product, if no match populate empty values
        matchFound = False
        for j in invfore:
            if i['asin'] == j['asin']:
                i.update(j)
                matchFound = True

        if not matchFound:
            empFore = emptyFore
            empFore['asin'] = i['asin']
            i.update(empFore)

    for i in prods:
        rowDict = {}
        for j in sales:
            if i['asin'] == j['asin']:
                i.update(j)

        for j in heads:
            datDict = {}
            datDict[j] = i[j]
            rowDict.update(datDict)

        outTable.append(rowDict)

    tableCols = []

    for i in headerNames:
        for j in heads:
            if j == 'asin':
                data = ('asin', tables.Column(verbose_name='ASIN'))
                tableCols.append(data)
            elif i['database_header'] == j:
                data = (i['database_header'], tables.Column(verbose_name=(i['amazon_header'])))
                tableCols.append(data)

    table = DataTable(outTable, extra_columns=tableCols)
    return(table)

@login_required
def index(request):
    """
    View function for home page of site.
    """
    return render(request, 'index.html', context = {})


def lot_of_saves(queryset):
    for item in queryset:
        item.save(force_update=True)

@login_required
@permission_required('product.can_input_data')
def data_input(request):
    """
    View function for the Data Input site
    """
    postdict = request.POST.dict()

    if 'prod_table' in postdict:
        typ = 'prod_table'
    elif 'sales_diag' in postdict:
        typ = 'sales_diag'
    elif 'inv_health' in postdict:
        typ = 'inv_health'
    elif 'spon_prod' in postdict:
        typ = 'spon_prod'
    elif 'inv_fore' in postdict:
        typ = 'inv_fore'

    if request.method == 'POST':
        dataset = Dataset()
        new_products = request.FILES['myfile']
        imported_data = dataset.load(new_products.read().decode('utf-8', errors='ignore'),format='csv')
        #verify that the input file has correct headers
        verified = verifyInput(imported_data, typ)

        if verified:
            amended_data = convertInput(imported_data, typ)

            if typ == 'prod_table':
                recordList = []

                for j in amended_data:
                    i = Product()
                    data = list(j)
                    i.asin = data[0]
                    i.product_name = data[1]
                    i.warehouse_units = data[2]
                    i.external_id = data[3]
                    i.released = data[4]
                    i.list_price = data[5]
                    i.product_group = data[6]
                    i.category = data[7]
                    i.sub_category = data[8]
                    i.model_number = data[9]
                    i.catalog_number = data[10]
                    i.replenishment_code = data[11]
                    i.page_view_rank = data[12]
                    i.brand_code = data[13]
                    i.vendor = data[14]

                    recordList.append(i)

                with transaction.atomic():
                    # Loop over each store and invoke save() on each entry
                    for i in recordList:
                        # save() method called on each member to create record
                        print(i.asin)
                        i.save()
            if typ == 'sales_diag':
                recordList = []

                for j in amended_data:
                    i = SalesDiagnostic()
                    data = list(j)
                    i.asin = data[0]
                    i.date = data[1]
                    i.asin_date = data[2]
                    i.product_name = data[3]
                    i.shipped_cogs = data[4]
                    i.shipped_cogs_perc = data[5]
                    i.shipped_cogs_prior_period = data[6]
                    i.shipped_cogs_last_year = data[7]
                    i.shipped_units = data[8]
                    i.shipped_units_perc = data[9]
                    i.shipped_units_prior_period = data[10]
                    i.shipped_units_last_year = data[11]
                    i.customer_returns = data[12]
                    i.free_replacements = data[13]
                    i.product = data[14]

                    recordList.append(i)

                with transaction.atomic():
                    # Loop over each store and invoke save() on each entry
                    for i in recordList:
                        # save() method called on each member to create record
                        print(i.asin)
                        i.save()
            if typ == 'inv_health':
                invhealth_resource = InventoryHealthResource()
                result = invhealth_resource.import_data(amended_data, dry_run=True)  # Test the data import
                if not result.has_errors():
                    invhealth_resource.import_data(amended_data, dry_run=False)  # Actually import now
                #else:
            if typ == 'spon_prod':
                sponprod_resource = SponsoredProductResource()
                result = sponprod_resource.import_data(amended_data, dry_run=True)  # Test the data import
                if not result.has_errors():
                    sponprod_resource.import_data(amended_data, dry_run=False)  # Actually import now
                #else:
            if typ == 'inv_fore':
                invfore_resource = InventoryForecastResource()
                result = invfore_resource.import_data(amended_data, dry_run=True)  # Test the data import
                if not result.has_errors():
                    invfore_resource.import_data(amended_data, dry_run=False)  # Actually import now

        else:
            print('Unverified')

    return render(request, 'data_input.html', context = {"message": 'sales_diag'})

@login_required
def report_view(request):
    """
    View function for the reporting output
    """
    repForm = ReportForm(request.user)

    return render(request, 'report.html', context={'repform':repForm, 'next': request.GET.get('next', '')})

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class Report(FormView):
    template_name = 'report.html'
    form_class = ReportForm

    def get(self, request):
        if 'vendor' in request.GET:
            form = ReportForm(request.user, request.GET)
            if form.is_valid():
                vendor = form.cleaned_data.get('vendor')
                entry_date = form.cleaned_data.get('report_date')
                heads = form.cleaned_data.get('headers')

                #Pull data for COGS chart and create json to pass information for chart
                dataset = SalesDiagnostic.objects.filter(date__lte=entry_date).filter(date__gte=entry_date-timedelta(days=6)).values('date').annotate(
                firstCol=Sum('shipped_cogs', filter=Q(date=entry_date-timedelta(days=6))),
                secondCol=Sum('shipped_cogs', filter=Q(date=entry_date-timedelta(days=5))),
                thirdCol=Sum('shipped_cogs', filter=Q(date=entry_date-timedelta(days=4))),
                fourthCol=Sum('shipped_cogs', filter=Q(date=entry_date-timedelta(days=3))),
                fifthCol=Sum('shipped_cogs', filter=Q(date=entry_date-timedelta(days=2))),
                sixthCol=Sum('shipped_cogs', filter=Q(date=entry_date-timedelta(days=1))),
                seventhCol=Sum('shipped_cogs', filter=Q(date=entry_date))).order_by('date')

                dates = list()
                t_6_series_data = list()
                t_5_series_data = list()
                t_4_series_data = list()
                t_3_series_data = list()
                t_2_series_data = list()
                yesterday_series_data = list()
                today_series_data = list()

                for entry in dataset:
                    dates.append('%s'  % entry['date'])
                    t_6_series_data.append(entry['firstCol'])
                    t_5_series_data.append(entry['secondCol'])
                    t_4_series_data.append(entry['thirdCol'])
                    t_3_series_data.append(entry['fourthCol'])
                    t_2_series_data.append(entry['fifthCol'])
                    yesterday_series_data.append(entry['sixthCol'])
                    today_series_data.append(entry['seventhCol'])

                t_6_series = {
                    'name': 'Date' + str(entry_date-timedelta(days=6)),
                    'data': t_6_series_data,
                    'color': 'green'
                }

                t_5_series = {
                    'name': 'Date' + str(entry_date-timedelta(days=5)),
                    'data': t_5_series_data,
                    'color': 'green'
                }

                t_4_series = {
                    'name': 'Date' + str(entry_date-timedelta(days=4)),
                    'data': t_4_series_data,
                    'color': 'green'
                }

                t_3_series = {
                    'name': 'Date' + str(entry_date-timedelta(days=3)),
                    'data': t_3_series_data,
                    'color': 'green'
                }

                t_2_series = {
                    'name': 'Date' + str(entry_date-timedelta(days=2)),
                    'data': t_2_series_data,
                    'color': 'green'
                }

                yesterday_series = {
                    'name': 'Date' + str(entry_date-timedelta(days=1)),
                    'data': yesterday_series_data,
                    'color': 'green'
                }

                today_series = {
                    'name': 'Date' + str(entry_date),
                    'data': today_series_data,
                    'color': 'green'
                }

                chart = {
                    'chart': {'type': 'column'},
                    'title': {'text': 'Shipped COGS by date'},
                    'xAxis': {'categories': dates},
                    'series': [t_6_series, t_5_series, t_4_series, t_3_series, t_2_series, yesterday_series, today_series]
                }

                dump = json.dumps(chart, cls=DecimalEncoder)

                table = create_data_output(vendor, entry_date, heads)
                RequestConfig(request, paginate={'per_page': 50}).configure(table)

                print(dataset)
                return render(request, 'output.html', {'vendor': vendor, 'table':table, 'chart': dump, 'repDate':entry_date})
        else:
            form = ReportForm(request.user)
        return render(request, 'report.html', {'form': form})

#@method_decorator(login_required, name='dispatch')
class Report_Output(View):

    def post(self, request):
        for i in request.POST.values():
            print(i)

    def get(self, request):
        return render(request, 'index.html')#, context = {'table':table, 'vendor': vendor})
