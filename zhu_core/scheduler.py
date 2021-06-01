from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from apps.connections import jobs as connections
from apps.users import jobs as users
from apps.tmu import jobs as tmu
from apps.loa import jobs as loa
from apps.mailer import jobs as mailer
from apps.training import jobs as training


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
        connections.notify_inactive_controllers,
        trigger=CronTrigger(day=23),  # Every 23rd date
        id='notify_inactive_controllers',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        users.sync_vatusa_roster,
        trigger=CronTrigger(minute=1),  # Top of every hour + 1
        id='sync_vatusa_roster',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        users.update_user_ratings,
        trigger=CronTrigger(minute=2),  # Top of every hour + 2
        id='update_user_ratings',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        tmu.fetch_metars,
        trigger=CronTrigger(minute=57),  # Every hour at x:57
        id='fetch_metars',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        tmu.delete_inactive_atis,
        trigger=CronTrigger(minute=4),  # Top of every hour + 4
        id='delete_inactive_atis',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        loa.update_loa_status,
        trigger=CronTrigger(hour=0),  # Every midnight
        id='update_loa_status',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        mailer.send_pending_mail,
        trigger=CronTrigger(minute='*/5'),  # Every 5 minutes
        id='send_pending_mail',
        max_instances=1,
        replace_existing=True
    )

    scheduler.add_job(
        mailer.clear_old_mail,
        trigger=CronTrigger(day_of_week='sat'),  # Every Saturday
        id='clear_old_mail',
        max_instances=1,
        replace_existing=True
    )

    scheduler.add_job(
        training.clear_expired_requests,
        trigger=CronTrigger(day_of_week='sat'),  # Every Saturday
        id='clear_expired_requests',
        max_instances=1,
        replace_existing=True
    )

    scheduler.start()
