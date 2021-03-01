from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from apps.connections import jobs as connections
from apps.users import jobs as users
from apps.tmu import jobs as tmu


def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        connections.update_online_controllers,
        trigger=CronTrigger(second=0),  # Top of every minute
        id='update_online_controllers',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        users.sync_vatusa_roster,
        trigger=CronTrigger(minute=0),  # Top of every hour
        id='sync_vatusa_roster',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        users.update_user_ratings,
        trigger=CronTrigger(minute=0),  # Top of every hour
        id='update_user_ratings',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        tmu.delete_inactive_atis,
        trigger=CronTrigger(minute=0),  # Top of every hour
        id='delete_inactive_atis',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        tmu.fetch_metars,
        trigger=CronTrigger(minute=0),  # Top of every hour
        id='fetch_metars',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()
