from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NewsArticle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("excerpt", models.TextField(blank=True, default="")),
                ("body", models.TextField(blank=True, default="")),
                ("image", models.URLField(blank=True, default="")),
                ("published_date", models.DateField()),
                ("is_published", models.BooleanField(default=False)),
                (
                    "category",
                    models.CharField(
                        choices=[("news", "News"), ("veranstaltung", "Veranstaltung")],
                        default="news",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "verbose_name": "News Article",
                "verbose_name_plural": "News Articles",
                "ordering": ["-published_date"],
            },
        ),
    ]
