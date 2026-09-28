from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_update_identity_autoincrement'),
    ]
    operations = [
        migrations.AddField(
            model_name='commonsettings',
            name='backend_url',
            field=models.CharField(default="http://0.0.0.0/", 
                                max_length=200, 
                                blank=False, 
			                    null=False,
                                help_text="URL of server (without port) hosting the backend."),
        ),   
        migrations.AddField(
            model_name='commonsettings',
            name='backend_port',
            field=models.IntegerField(default=80, help_text='Port from which the system is served', verbose_name='Backend port'),
        ),
        migrations.AddField(
            model_name='commonsettings',
            name='override_backend_port',
            field=models.BooleanField(default=True, help_text='If checked, the system will override the default port and use the value of Backend port'),
        ),
    ]