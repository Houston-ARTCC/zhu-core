import os
from discord_webhook import DiscordWebhook, DiscordEmbed
from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.events.models import Event


@receiver(pre_save, sender=Event)
def post_event_webhook(instance, **kwargs):
    """
    This signal posts an embedded message in the designated
    events Discord channel when an event is set to visible.
    """
    old_instance = Event.objects.filter(id=instance.id)

    if not old_instance.exists():
        return

    if old_instance.first().hidden and not instance.hidden:
        url = f'https://www.zhuartcc.org/events/{instance.id}'
        webhook = DiscordWebhook(url=os.getenv('EVENTS_WEBHOOK_URL'))
        embed = DiscordEmbed(
            title=f':calendar: {instance.name}',
            description=instance.description + f'\n**[Sign up for the event here!]({url})**',
            color='109cf1',
        )
        embed.add_embed_field(
            name='Start & End',
            value=f'{instance.start.strftime("%b %d, %Y @ %H%Mz")} - {instance.end.strftime("%b %d, %Y @ %H%Mz")}',
            inline=False,
        )
        embed.add_embed_field(
            name='Presented by',
            value=instance.host,
        )
        embed.set_image(url=instance.banner)
        webhook.add_embed(embed)
        webhook.execute()
