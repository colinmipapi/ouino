# Generated by Django 3.0.7 on 2020-06-12 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0004_question_response_message_ts'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
