import os
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.utils import timezone


class Status(models.IntegerChoices):
    PENDING = 0, 'Pending'
    FAILED = 1, 'Failed'
    SENT = 2, 'Sent'


class Email(models.Model):
    subject = models.CharField(max_length=255)
    html_body = models.TextField()
    text_body = models.TextField()
    from_email = models.EmailField(null=True)
    to_email = models.TextField()
    cc_email = models.TextField(null=True)
    bcc_email = models.TextField(null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.PENDING)
    last_attempt = models.DateTimeField(null=True)

    def send(self):
        try:
            EmailMultiAlternatives(
                subject=self.subject,
                to=[self.to_email.split(',')],
                cc=[self.cc_email.split(',')],
                bcc=[self.bcc_email.split(',')],
                from_email=self.from_email or os.getenv('EMAIL_ADDRESS'),
                body=self.text_body,
                alternatives=[(self.html_body, 'text/html')],
            ).send()
            self.status = Status.SENT
        except:
            self.status = Status.FAILED

        self.last_attempt = timezone.now()
        self.save()
