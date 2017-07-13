# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-30 12:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('finance', '0001_initial'),
        ('coordinates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='arrivage',
            name='devise',
            field=models.ForeignKey(help_text='Devise principale', null=True, on_delete=django.db.models.deletion.CASCADE, to='finance.Currency'),
        ),
        migrations.AddField(
            model_name='arrivage',
            name='lieu_provenance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coordinates.Localite', verbose_name='Localité'),
        ),
        migrations.AddField(
            model_name='arrivage',
            name='pays',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coordinates.Pays'),
        ),
        migrations.AddField(
            model_name='adresse',
            name='localite',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinates.Localite'),
        ),
        migrations.AddField(
            model_name='adresse',
            name='pays',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinates.Pays'),
        ),
        migrations.AddField(
            model_name='contactphone',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinates.Contact'),
        ),
    ]
