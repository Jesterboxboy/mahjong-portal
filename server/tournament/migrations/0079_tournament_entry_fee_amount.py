from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0078_alter_tournamentemailtemplate_email_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournament",
            name="entry_fee_amount",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="In €, shown on the announcement page",
                max_digits=6,
                null=True,
                verbose_name="Entry fee amount",
            ),
        ),
    ]
