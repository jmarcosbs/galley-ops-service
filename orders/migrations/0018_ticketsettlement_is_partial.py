from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0017_ticketsettlementitem_charged_half_portion"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketsettlement",
            name="is_partial",
            field=models.BooleanField(default=False),
        ),
    ]

