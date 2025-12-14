from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0006_customdish"),
    ]

    operations = [
        migrations.AddField(
            model_name="dish",
            name="show_on_public_menu",
            field=models.BooleanField(
                default=False,
                help_text="Controla se o item aparece na landing page pública.",
                verbose_name="mostrar no cardápio público",
            ),
        ),
    ]
