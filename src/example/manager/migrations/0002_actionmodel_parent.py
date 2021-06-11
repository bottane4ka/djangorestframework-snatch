# Generated by Django 3.2.4 on 2021-06-04 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("manager", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="actionmodel",
            name="parent",
            field=models.ForeignKey(
                db_column="parent_id",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="action_list",
                to="manager.actionmodel",
                verbose_name="Родительское действие",
            ),
        )
    ]
