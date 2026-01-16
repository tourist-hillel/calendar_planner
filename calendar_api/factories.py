import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
# from events.models import Event
# from categories.models import Category
from faker import Faker
import pytz
from datetime import timedelta

fake = Faker()
# User = get_user_model()
tz = pytz.UTC

class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('cell_phone', )

    cell_phone = factory.Sequence(lambda n: f'+380{n:06d}')
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.Faker('last_name')
    # password = factory.PostGenerationMethodCall('set_password', fake.password())
    email = factory.Faker('email')
    preffered_lang = 'uk'
    is_active = True
    is_staff = False
    is_superuser = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop('password', 'TestPass123')
        user = super()._create(model_class, *args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = 'categories.Category'

    name = factory.Faker('word')
    color = factory.Faker('hex_color')


class EventFactory(DjangoModelFactory):
    class Meta:
        model = 'events.Event'

    title = factory.LazyAttribute(lambda _:  fake.sentence(nb_words=5)[:100])
    description = factory.Faker('paragraph')
    start_time = factory.Faker('future_datetime', tzinfo=tz)
    end_time = factory.LazyAttribute(
        lambda o: o.start_time + timedelta(days=5)
    )
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    is_completed = False
