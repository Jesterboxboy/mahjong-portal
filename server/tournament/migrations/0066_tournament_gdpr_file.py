# Generated manually

from django.db import migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0065_tournamentapplication_additional_info_optional"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournament",
            name="gdpr_file",
            field=filebrowser.fields.FileBrowseField(
                blank=True,
                directory="gdpr/",
                extensions=[".pdf", ".doc", ".docx"],
                max_length=200,
                null=True,
                verbose_name="GDPR document (from media library)",
            ),
        ),
    ]
