# Generated by Django 2.0.4 on 2018-05-05 21:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0009_remove_salesdiagnostic_products'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Products',
            new_name='Product',
        ),
        migrations.AddField(
            model_name='salesdiagnostic',
            name='product',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='reporting.Product'),
            preserve_default=False,
        ),
    ]
