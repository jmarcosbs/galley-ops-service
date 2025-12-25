from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0008_categorytranslation_dishtranslation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sidedishoption",
            name="default_side_dish",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="default_for_side_dish_options",
                to="menu.sidedish",
                verbose_name="acompanhamento padrão",
            ),
        ),
    ]
