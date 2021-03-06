import uuid
import datetime

from django.db import models
from django.contrib.postgres.fields import JSONField


# Create your models here.
class Question(models.Model):

    CHOICES = (
        ('U', 'Urgent'),
        ('N', 'Normal'),
        ('W', 'Whenever')
    )

    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    created = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True
    )
    created_by = models.CharField(
        max_length=100,
    )
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    status = models.CharField(
        choices=CHOICES,
        max_length=2,
        blank=True,
        null=True
    )
    question_text = models.CharField(
        max_length=140,
    )
    channel_id = models.CharField(
        max_length=100,
    )
    responses = JSONField(
        blank=True,
        null=True
    )
    message_ts = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    response_message_ts = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.question_text

    @property
    def reminder_time(self):
        if self.status == 'U':
            remind = datetime.timedelta(hours=2, minutes=45)
        elif self.status == 'N':
            remind = datetime.timedelta(hours=23, minutes=45)
        elif self.status == 'W':
            remind = datetime.timedelta(hours=71, minutes=45)
        else:
            remind = None
        return remind
