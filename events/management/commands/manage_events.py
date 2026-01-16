from typing import Any
from django.core.management.base import BaseCommand, CommandError, CommandParser
from events.models import Event
from categories.models import Category
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
LIST = 'list'
CREATE = 'create'
DELETE = 'delete'
COMPLETE = 'complete'

ALLOWED_COMMANDS = [
    LIST,
    CREATE,
    DELETE,
    COMPLETE
]


class Command(BaseCommand):
    help = f'Manage events with subcommands: {", ".join(ALLOWED_COMMANDS)}'

    def add_arguments(self, parser: CommandParser) -> None:
        subparser = parser.add_subparsers(dest='subcommand', required=True)

        list_parser = subparser.add_parser(
            LIST,
            help='List all events'
        )
        list_parser.add_argument(
            '--not-completed',
            action='store_true'
        )
        list_parser.add_argument(
            '--completed',
            action='store_true'
        )

        create_parser = subparser.add_parser(
            CREATE,
            help='Create a new event'
        )
        create_parser.add_argument(
            'user_id',
            type=int,
            help='User ID'
        )
        create_parser.add_argument(
            'category_id',
            type=int,
            help='Category ID'
        )
        create_parser.add_argument(
            '--count',
            type=int,
            help='Count of events to create'
        )

        delete_parser = subparser.add_parser(
            DELETE,
            help='Delete event'
        )
        delete_parser.add_argument(
            'event_ids',
            type=int,
            nargs='+',
            help="ID's of events to delete"
        )

        complete_parses = subparser.add_parser(
            COMPLETE,
            help='Complete event'
        )
        complete_parses.add_argument(
            'event_ids',
            type=int,
            nargs='+',
            help="ID's of events to complete"
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        subcommand = options.get('subcommand')

        if subcommand not in ALLOWED_COMMANDS:
            raise CommandError('Invalid subcommand')

        if subcommand == LIST:
            self._handle_list(options)
        elif subcommand == CREATE:
            self._handle_create(options)
        elif subcommand == DELETE:
            self._handle_delete(options)
        elif subcommand == COMPLETE:
            self._handle_complete(options)
    
    def _handle_list(self, options):
        events = Event.objects.all()

        not_completed_flag = options.get('not_completed')
        completed_flag = options.get('completed')
        if all([completed_flag, not_completed_flag]):
            raise CommandError('Cannot use both --not-completed and --completed in one execution flow')
        
        if not_completed_flag:
            events = events.filter(is_completed=False)
        if completed_flag:
            events = events.filter(is_completed=True)
        
        if not events:
            self.stdout.write(self.style.WARNING('No events found'))
            return

        self.stdout.write(self.style.SUCCESS('List of events:'))
        for event in events:
            self.stdout.write(self.style.SUCCESS(
                f'- {event.title}|Deadline: {event.end_time}|Assigned user: {event.user}'
            ))

    def _handle_create(self, options):
        try:
            user = User.objects.get(id=options['user_id'])
            category = Category.objects.get(id=options['category_id'])
        except (User.DoesNotExist, Category.DoesNotExist, ValueError) as e:
            raise CommandError(f'The following error caused: {e}')
        
        count = options.get('count') or 1
        fake = Faker()

        for _ in range(count):
            Event.objects.create(
                title = fake.sentence(nb_words=5)[:-1],
                description = fake.paragraph(),
                start_time = fake.date_this_century(),
                end_time = fake.date_this_century(),
                user = user,
                category = category,
                is_completed = fake.boolean(chance_of_getting_true=25)
            )
        self.stdout.write(self.style.SUCCESS(f'Created {count} events for user {user} with category {category}'))

    def _handle_delete(self, options):
        events_ids = options.get('event_ids')
        delete_count = 0

        for event_id in events_ids:
            try:
                event = Event.objects.get(id=event_id)
                title = event.title
                event.delete()
                delete_count += 1
                self.stdout.write(self.style.SUCCESS(f'Deleted event with ID {event_id}: {title}'))
            except Event.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Event with ID={event_id} not found. Skipping!'))

        if delete_count == 0:
            raise CommandError('No event were deleted!!')
        
    def _handle_complete(self, options):
        events_ids = options.get('event_ids')

        for event_id in events_ids:
            try:
                event = Event.objects.get(id=event_id)
                event.is_completed = True
                event.save()
                self.stdout.write(self.style.SUCCESS(f'Completed event with ID {event_id}: {event.title}'))
            except Event.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Event with ID={event_id} not found. Skipping!'))
           