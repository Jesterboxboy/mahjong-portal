# Generated manually — removes the game_type column that was added directly to
# the DB but never cleanly tracked in the migration history.
# We use RunSQL to drop the column only if it exists, so this is safe to replay.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("austria_ranking", "0007_alter_qualificationmodeinfo_info_text_de_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE austria_ranking_ematournamentresult DROP COLUMN IF EXISTS game_type;",
            reverse_sql="ALTER TABLE austria_ranking_ematournamentresult ADD COLUMN game_type smallint NOT NULL DEFAULT 0;",
        ),
    ]
