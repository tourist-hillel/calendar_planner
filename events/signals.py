from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver, Signal
from events.models import Event, EventActions, EventLog
from datetime import datetime, timezone

custom_signal = Signal()

# @receiver(pre_save, sender=Event)
# def check_end_date(sender, instance, **kwargs):
#     if instance.end_time and instance.end_time < datetime.now().replace(tzinfo=timezone.utc):
#         instance.is_completed = True

@receiver(pre_save, sender=Event)
@receiver(post_save, sender=Event)
def event_log(sender, instance, created=False, **kwargs):
    if instance.pk:
        object_id = instance.pk
        old_event = Event.objects.get(id=object_id)
        if kwargs['signal'] is post_save:
            if created:
                action = EventActions.CREATED
            else:
                action = EventActions.UPDATED
            
            EventLog.objects.create(
                action=action,
                model=sender.__name__,
                object_id=object_id
            )

        if instance.is_completed and old_event.is_completed is False:
            EventLog.objects.create(
                action=EventActions.COMPLETED,
                model=sender.__name__,
                object_id=object_id
            )

@receiver(custom_signal)
def log_record(sender, action, user, **kwargs):
    EventLog.objects.create(
                action=action,
                model=sender.__name__,
                object_id=user.id
            )