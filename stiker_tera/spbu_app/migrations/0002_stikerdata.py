# Generated by Django 4.2.20 on 2025-04-08 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spbu_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StikerData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=100)),
                ('tanggal', models.DateField()),
                ('jumlah', models.IntegerField()),
            ],
        ),
    ]
