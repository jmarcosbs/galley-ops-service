from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0014_alter_ticketsettlement_canceled"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketsettlement",
            name="nfce_last_consult_payload",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ticketsettlement",
            name="nfce_last_status_code",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="ticketsettlement",
            name="nfce_last_status_message",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
