from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0017_dishorder_charge_half_portion_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketsettlementitem",
            name="charged_half_portion",
            field=models.BooleanField(default=False),
        ),
    ]

