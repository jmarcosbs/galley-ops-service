from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0011_rename_nfce_issued_at_ticketsettlement_nfce_authorization_datetime_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="is_outside",
            field=models.BooleanField(default=False),
        ),
    ]
