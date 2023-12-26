from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import DateTimeField, ExpressionWrapper, F, Prefetch

from apps.events.models import EventScore, PositionShift
from apps.feedback.models import Feedback
from apps.users.models import Status, User


class Command(BaseCommand):
    help = "Calculates event scores"  # noqa: A003

    def handle(self, *args, **options):
        for user in User.objects.filter(status=Status.ACTIVE).prefetch_related(
            Prefetch(
                "event_shifts",
                queryset=PositionShift.objects.all().select_related("position__event"),
            ),
            Prefetch("event_scores"),
        ):
            for event in {shift.position.event for shift in user.event_shifts.all()}:
                if user.event_scores.filter(event=event).exists():
                    # Score has already been calculated for this event
                    continue

                # This will fetch the positions again, but this route is expected
                # to be taken far less often than the "continue"
                shifts = user.event_shifts.filter(position__event=event)
                target_duration = sum((shift.end - shift.start).total_seconds() for shift in shifts)

                sessions = user.sessions.annotate(
                    end_time=ExpressionWrapper(F("start") + F("duration"), output_field=DateTimeField()),
                ).filter(
                    # Session ended after the event started
                    end_time__gt=event.start,
                    # Session started before the event ended
                    start__lt=event.end,
                )
                actual_duration = sum(
                    (min(session.end, event.end) - max(session.start, event.start)).total_seconds()
                    for session in sessions
                )
                extra_duration = sum(session.duration.total_seconds() for session in sessions) - actual_duration

                # Percentage of event time controlled, with up to an hour
                # of "extra credit" for controlling before and after the event
                total_duration = actual_duration + min(extra_duration, 3600)
                controlling_score = total_duration / target_duration * 100

                # Awards additional points on score for positive (4 or 5 stars) feedback,
                # and deducts points for negative (1 or 2 stars) feedback.
                feedback_score = 0
                feedback_notes = []
                for feedback in Feedback.objects.filter(controller=user, event=event, approved=True):
                    feedback_score += (feedback.rating - 3) * 5
                    feedback_notes.append({"rating": feedback.rating})

                score = controlling_score + feedback_score
                notes = {
                    "target_duration": target_duration,
                    "total_duration": total_duration,
                    "feedback": feedback_notes,
                }

                EventScore.objects.create(event=event, user=user, score=score, notes=notes)

        print(f"{datetime.now()} :: calculate_scores :: SUCCESS")
