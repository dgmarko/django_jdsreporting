# Generated by Django 2.0.4 on 2018-05-03 16:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0004_vendorasin'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesDiagnostic',
            fields=[
                ('asin_date', models.CharField(help_text='ASIN_Date Combo for the entry', max_length=50, primary_key=True, serialize=False, verbose_name='ASIN_Date Combined')),
                ('date', models.DateField(help_text='Date Released')),
                ('shipped_cogs', models.DecimalField(blank=True, decimal_places=2, help_text='Shipped Cost of Goods Sold', max_digits=14, null=True)),
                ('shipped_cogs_perc', models.DecimalField(blank=True, decimal_places=5, help_text='Shipped Cost of Goods Sold Percentage of Total', max_digits=8, null=True)),
                ('shipped_cogs_prior_period', models.DecimalField(blank=True, decimal_places=2, help_text='Shipped Cost of Goods Sold Change From Prior Period', max_digits=14, null=True)),
                ('shipped_cogs_last_year', models.DecimalField(blank=True, decimal_places=5, help_text='Shipped Cost of Goods Sold Change From Last Year', max_digits=8, null=True)),
                ('shipped_units', models.IntegerField(blank=True, help_text='Shipped Units', null=True)),
                ('shipped_units_perc', models.DecimalField(blank=True, decimal_places=5, help_text='Shipped Units Percentage of Total', max_digits=8, null=True)),
                ('shipped_units_prior_period', models.DecimalField(blank=True, decimal_places=2, help_text='Shipped Units Change From Prior Period', max_digits=14, null=True)),
                ('shipped_units_last_year', models.DecimalField(blank=True, decimal_places=5, help_text='Shipped Units Change From Last Year', max_digits=8, null=True)),
                ('customer_returns', models.IntegerField(blank=True, help_text='Customer Returns', null=True)),
                ('free_replacements', models.IntegerField(blank=True, help_text='Free Replacements', null=True)),
                ('asin', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='reporting.Products')),
            ],
            options={
                'permissions': (('can_input_data', 'Able to Input Data'),),
            },
        ),
    ]