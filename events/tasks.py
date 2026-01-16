import os
import json
import logging
from celery import shared_task
from django.conf import settings
from django.db.models.query import QuerySet
from datetime import datetime
from events.models import Event

logger = logging.getLogger(__name__)

def prepare_event_context(event_data: Event| QuerySet):
    def fill_context(event_obj):
        context = {
            'event_id': event_obj.pk,
            'title': event_obj.title,
            'start_time': str(event_obj.start_time),
            'end_time': str(event_obj.end_time),
            'created_at': str(event_obj.created_at),
            'user': str(event_obj.user),
            'category': str(event_obj.category),
            'is_completed': event_obj.is_completed
        }
        return context
    event_context = None
    if isinstance(event_data, QuerySet):
        event_context = [fill_context(event) for event in event_data]
    if isinstance(event_data, Event):
        event_context = fill_context(event_data)
    return event_context or {}


@shared_task
def log_new_event(event_id: int) -> None:
    logger.info(f'Starting "log_new_event" task with provided event_id: {event_id}')
    try:
        event = Event.objects.get(id=event_id)
        logger.info(f'Event found: {event.title} by user {event.user}')
        context = prepare_event_context(event)
        logger.debug(f'Context for task recived: {str(context)}', exc_info=True)
        output_path = os.path.join(settings.MEDIA_ROOT, 'statistics', f'event_{event_id}.json')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as event_file:
            json.dump(context, event_file, indent=4, ensure_ascii=False)
        logger.info(f'Successfuly saved event {event_id} detail to {output_path}')
    except Event.DoesNotExist:
        logger.warning(f'Event {event_id} does not exists')
        pass
    except Exception as e:
        logger.error(f'Error in "log_new_event" view: {str(e)}', exc_info=True)
        raise


@shared_task
def events_report():
    events = Event.objects.all()
    completed = events.filter(is_completed=True)
    not_completed = events.filter(is_completed=False)

    report_context = {
        'total_events': events.count(),
        'completed': {
            'total': completed.count(),
            'events': prepare_event_context(completed)
        },
        'not_completed': {
            'total': not_completed.count(),
            'events': prepare_event_context(not_completed)
        }
    }
    output_path = os.path.join(settings.MEDIA_ROOT, 'statistics', f'event_report{datetime.now().isoformat()}.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as event_file:
        json.dump(report_context, event_file, indent=4, ensure_ascii=False)