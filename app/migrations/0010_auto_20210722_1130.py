# Generated by Django 2.2.10 on 2021-07-22 06:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20210721_2027'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Title', models.TextField(blank=True, verbose_name='Title')),
                ('Breif', models.TextField(blank=True, verbose_name='Brief')),
                ('Picture', models.ImageField(blank=True, default='New_image/default-news.png', upload_to='New_image')),
                ('Link', models.URLField()),
            ],
        ),
        migrations.AlterField(
            model_name='accessrequest',
            name='Request_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 7, 22, 11, 30, 22, 599350), null=True, verbose_name='Date of Request'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='Invoice_Date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 7, 22, 11, 30, 22, 598753), null=True, verbose_name='Date of invoice'),
        ),
    ]
