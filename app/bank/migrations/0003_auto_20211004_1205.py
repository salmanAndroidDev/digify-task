# Generated by Django 3.2.5 on 2021-10-04 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('bank', '0002_auto_20211004_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers', to='bank.branch'),
        ),
        migrations.AlterField(
            model_name='account',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='accounts.user'),
        ),
    ]