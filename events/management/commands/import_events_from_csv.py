import csv
from django.core.management.base import BaseCommand, CommandError, CommandParser
from events.models import Event
from categories.models import Category
from django.contrib.auth import get_user_model
from datetime import datetime
from tqdm import tqdm

User = get_user_model()


class Command(BaseCommand):
    help = 'Import events from csv file'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Test run without saving'
        )

    def handle(self, *args, **options) -> str | None:
        csv_file = options['csv_file']
        dry_run = options['dry_run']


        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
        except FileNotFoundError:
            raise CommandError(f'File {csv_file} not found!!!')
        
        if not rows:
            self.stdout.write(self.style.WARNING('CSV file is empty!'))

        create_count = {
            'events': 0,
            'categories': 0
        }
        errors = []

        with tqdm(total=len(rows), desc='Importing events...', unit='event') as pbar:
            for row in rows:
                try:
                    user = User.objects.get(id=row['user_id'])
                    if row['category_id']:
                        category = Category.objects.get(id=row['category_id'])
                    else:
                        # category, _ = Category.objects.get_or_create(name=row['category'])
                        category = Category.objects.filter(name=row['category']).first()
                    if not category:
                        category = Category(
                            name=row['category']
                        )
                        create_count['categories'] += 1
                    start_time = datetime.strptime(row.get('start_time'), '%Y-%m-%d')
                    end_time = datetime.strptime(row.get('end_time'), '%Y-%m-%d')

                    event = Event(
                        title = row['title'],
                        description = row['description'],
                        start_time = start_time,
                        end_time = end_time,
                        is_completed = row['is_completed'].lower() == 'true',
                        user = user,
                        category = category
                    )
                    if not dry_run:
                        category.save()
                        event.save()
                    create_count['events'] += 1
                except (User.DoesNotExist, Category.DoesNotExist, ValueError) as e:
                    errors.append(f'| Error in row: {row} \nerror: {e}|')
                pbar.update(1)
        self.stdout.write(self.style.SUCCESS(
            f'|Events {create_count["events"]}| \n|Categories: {create_count["categories"]}| \n|dry-run: {dry_run}|'
        ))
        if errors:
            self.stdout.write(self.style.ERROR('Errors:'))
            for error in errors:
                 self.stdout.write(self.style.ERROR(error))