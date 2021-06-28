import os
from discord_webhook import DiscordWebhook, DiscordEmbed
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.events.models import Event


@receiver(pre_save, sender=Event)
def event_webhook_edited(instance, **kwargs):
    """
    This signal posts an embedded message in the designated
    events Discord channel when an event is set to visible.
    """
    if instance.hidden or instance.id is None:
        return

    old_instance = Event.objects.filter(id=instance.id)
    if old_instance.exists() and not old_instance.first().hidden:
        return

    post_event_webhook(instance)


@receiver(post_save, sender=Event)
def event_webhook_created(instance, created, **kwargs):
    """
    This signal posts an embedded message in the designated
    events Discord channel when an event is created as visible.
    """
    if created and not instance.hidden:
        post_event_webhook(instance)


def post_event_webhook(event):
    if os.getenv('EVENTS_WEBHOOK_URL') is None:
        return

    url = f'https://www.zhuartcc.org/events/{event.id}'
    webhook = DiscordWebhook(url=os.getenv('EVENTS_WEBHOOK_URL'))
    embed = DiscordEmbed(
        title=f':calendar: {event.name}',
        description=str(event.description) + f'\n**[Sign up for the event here!]({url})**',
        color='109cf1',
    )
    embed.add_embed_field(
        name='Start & End',
        value=f'{event.start.strftime("%b %d, %Y @ %H%Mz")} - {event.end.strftime("%b %d, %Y @ %H%Mz")}',
        inline=False,
    )
    embed.add_embed_field(
        name='Presented by',
        value=event.host,
    )
    embed.set_image(url=event.banner)
    webhook.add_embed(embed)
    webhook.execute()
