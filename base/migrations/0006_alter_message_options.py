# Generated by Django 4.0.3 on 2023-11-05 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_remove_room_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['-created']},
        ),
    ]