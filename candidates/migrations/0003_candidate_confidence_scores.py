# Generated manually for adding confidence_scores field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0002_candidate_designation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='confidence_scores',
            field=models.JSONField(blank=True, null=True),
        ),
    ]

