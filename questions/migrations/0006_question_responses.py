# Generated by Django 3.0.7 on 2020-06-12 16:42

import django.contrib.postgres.fields.hstore
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0005_question_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='responses',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True),
        ),
    ]
