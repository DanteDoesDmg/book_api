# Generated by Django 3.0.8 on 2020-08-02 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_auto_20200801_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='google_id',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='book_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
