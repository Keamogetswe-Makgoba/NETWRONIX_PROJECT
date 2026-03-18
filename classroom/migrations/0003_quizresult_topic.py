

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0002_quizresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizresult',
            name='topic',
            field=models.CharField(default='General', max_length=255),
        ),
    ]
