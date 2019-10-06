# Generated by Django 2.2.5 on 2019-10-05 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handwriting', '0004_dataset'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='kind',
            field=models.CharField(choices=[('digits', 'Numbers from 0 to 9'), ('cyrillic', 'Macedonian cyrillic charactere А-Ш, а-ш'), ('latin', 'Latin characters A-Z, a-z')], default='digits', max_length=32),
        ),
    ]