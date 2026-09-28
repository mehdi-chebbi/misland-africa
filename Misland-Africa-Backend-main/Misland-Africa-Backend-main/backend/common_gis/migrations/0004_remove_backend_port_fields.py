from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common_gis', '0003_auto_update_identity_autoincrement'),
    ]
    operations = [
         migrations.RemoveField(
            model_name='gissettings',
            name='backend_url',
        ),
        migrations.RemoveField(
            model_name='gissettings',
            name='override_backend_port',
        ),
        migrations.RemoveField(
            model_name='gissettings',
            name='backend_port',
        ),
    ]