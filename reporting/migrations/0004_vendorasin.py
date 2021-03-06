# Generated by Django 2.0.4 on 2018-05-03 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0003_checks'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorASIN',
            fields=[
                ('asin', models.CharField(help_text='ASIN for the product', max_length=50, primary_key=True, serialize=False, verbose_name='ASIN')),
                ('vendor', models.CharField(help_text='Vendor for the ASIN', max_length=50, verbose_name='Vendor')),
            ],
            options={
                'permissions': (('can_add_new_vendors', 'Able to add Vendor ASIN Checks'),),
            },
        ),
    ]
