# Generated by Django 2.1.5 on 2019-03-30 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0005_taskdetail_task_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskdetail',
            name='result',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]