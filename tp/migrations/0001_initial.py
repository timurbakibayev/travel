# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-29 07:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateField(auto_now=True)),
                ('text', models.CharField(max_length=10000)),
            ],
            options={
                'ordering': ['entry_date'],
            },
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination', models.CharField(max_length=1000, verbose_name='Destination')),
                ('entry_date', models.DateField(auto_now=True)),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(verbose_name='End Date')),
            ],
            options={
                'ordering': ['start_date'],
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='trip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tp.Trip'),
        ),
    ]
