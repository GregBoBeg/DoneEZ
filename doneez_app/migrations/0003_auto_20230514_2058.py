# Generated by Django 3.1.5 on 2023-05-15 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doneez_app', '0002_auto_20230426_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesstype',
            name='business_type_tagline',
            field=models.CharField(blank=True, help_text='Provide a short tagline to describe the Business Type.', max_length=100, null=True, verbose_name='Business Type Tagline'),
        ),
        migrations.AlterField(
            model_name='businesstype',
            name='b2b',
            field=models.CharField(choices=[('RETAIL', 'Retail'), ('SUPPLIER', 'Supplier'), ('SOLUTION', 'Solution')], default='RETAIL', help_text='Indicates the type of business and where the business will show up.  "Retail" businesses are displayed in end-consumer searches. "Supplier" businesses are displayed in Supplier Searches.  "Solution" businesses are displayed on the Solutions page.', max_length=10, verbose_name='B2B'),
        ),
    ]
