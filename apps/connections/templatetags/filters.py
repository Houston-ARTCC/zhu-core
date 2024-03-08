from django import template

register = template.Library()


@register.filter()
def timedelta_hours(td):
    """
    Returns a truncated integer for the hours in the
    timedelta object.
    """
    return int(td.total_seconds() / 3600)


@register.filter()
def format_timedelta(td):
    """
    Format a timedelta object with the format {hours}h {minutes}m.
    """
    if td is None:
        return "0h 0m"

    seconds = td.total_seconds()
    hours, seconds = divmod(seconds, 3600)
    minutes = seconds / 60
    return f"{int(hours)}h {int(minutes)}m"
