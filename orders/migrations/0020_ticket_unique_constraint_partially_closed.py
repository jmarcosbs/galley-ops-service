from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0019_alter_ticket_status"),
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
                condition=models.Q(("status__in", ["open", "partially_paid"])),
                name="unique_open_ticket_number",
            ),
        ),
    ]
