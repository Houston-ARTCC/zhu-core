import os
import traceback
from smtplib import SMTPException

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.utils import timezone


class Status(models.IntegerChoices):
    PENDING = 0, "Pending"
    FAILED = 1, "Failed"
    SENT = 2, "Sent"


class Email(models.Model):
    subject = models.CharField(max_length=255)
    html_body = models.TextField()
    text_body = models.TextField()
    from_email = models.EmailField(null=True)
    to_email = models.TextField()
    cc_email = models.CharField(max_length=255, null=True)
    bcc_email = models.CharField(max_length=255, null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.PENDING)
    last_attempt = models.DateTimeField(null=True)
    error = models.TextField(null=True)

    def send(self):
        if (cc := self.cc_email) is not None:
            cc = cc.split(",")

        if (bcc := self.bcc_email) is not None:
            bcc = bcc.split(",")

        try:
            EmailMultiAlternatives(
                subject=self.subject,
                to=self.to_email.split(","),
                cc=cc,
                bcc=bcc,
                from_email=self.from_email or os.getenv("EMAIL_ADDRESS"),
                body=self.text_body,
                alternatives=[(self.html_body, "text/html")],
            ).send()
            self.status = Status.SENT
            self.error = None
        except SMTPException:
            self.status = Status.FAILED
            self.error = traceback.format_exc()

        self.last_attempt = timezone.now()
        self.save()
