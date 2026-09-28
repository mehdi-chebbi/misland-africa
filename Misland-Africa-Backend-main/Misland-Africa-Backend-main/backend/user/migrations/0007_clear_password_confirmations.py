from django.db import migrations


def clear_password_confirmations(apps, schema_editor):
    CustomUser = apps.get_model("user", "CustomUser")
    CustomUser.objects.exclude(password2="").update(password2="")


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0006_auto_20221221_0740"),
    ]

    operations = [
        migrations.RunPython(clear_password_confirmations, migrations.RunPython.noop),
    ]
