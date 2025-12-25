from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0015_ticketsettlement_nfce_last_consult_fields"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="ticket",
            name="unique_open_ticket_number",
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.UniqueConstraint(
                fields=("number", "is_outside"),
                condition=models.Q(("status", "open")),
                name="unique_open_ticket_number",
            ),
        ),
    ]
