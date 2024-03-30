import os
import traceback
from smtplib import SMTPException
from typing import Any

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone


class Status(models.IntegerChoices):
    PENDING = 0, "Pending"
    FAILED = 1, "Failed"
    SENT = 2, "Sent"


class EmailManager(models.Manager):
    def queue(
        self,
        *,
        to,
        subject: str,
        from_email: str,
        template: str,
        context: dict[str, Any] | None = {},
        cc=None,
    ):
        context.update(user=to, subject=subject)

        Email.objects.create(
            subject=subject,
            html_body=render_to_string(f"{template}.html", context=context),
            text_body=render_to_string(f"{template}.txt", context=context),
            from_email=from_email,
            to_email=to.email,
            cc_email=cc.email if cc is not None else None,
        )


class Email(models.Model):
    objects = EmailManager()

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
