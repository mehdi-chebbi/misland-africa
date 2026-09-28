import common_gis.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common_gis", "0011_auto_20250523_0537"),
    ]

    operations = [
        migrations.AlterField(
            model_name="publishedcomputationyear",
            name="published_year",
            field=models.PositiveIntegerField(
                default=common_gis.models.current_year,
                validators=[
                    django.core.validators.MinValueValidator,
                    common_gis.models.max_year_validator,
                ],
            ),
        ),
        migrations.AlterField(
            model_name="raster",
            name="raster_year",
            field=models.PositiveIntegerField(
                default=common_gis.models.current_year,
                help_text="Year",
                validators=[
                    django.core.validators.MinValueValidator,
                    common_gis.models.max_year_validator,
                ],
            ),
        ),
    ]
