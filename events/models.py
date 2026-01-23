from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from categories.models import Category
# from calendar_accounts.models import CalendarUser
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Event(models.Model):
    title = models.CharField(max_length=140, verbose_name=_('Назва події'))
    description = models.TextField(blank=True, verbose_name=_('Опис події'))
    start_time = models.DateTimeField(verbose_name=_('Дата та час початку'))
    end_time = models.DateTimeField(verbose_name=_('Дата та час закінчення'))
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Користувач'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name=_('Категорія'))
    is_completed = models.BooleanField(default=False, verbose_name=_('Виконано'))
    short_description = models.CharField(max_length=140, blank=True, verbose_name=_('Короткий опис'))
    event_category = models.ForeignKey('events.Category', on_delete=models.SET_NULL, null=True)
    short_description = models.CharField(max_length=140, blank=True, verbose_name=_('Короткий опис'))

    def __str__(self) -> str:
        return f'{self.title} - created: {self.created_at}'
    
    class Meta:
        verbose_name = _('Подія')
        verbose_name_plural = _('Події')
        permissions = [
            ('can_see_all_events', 'Може переглядати всі події'),
            ('can_edit_all_events', 'Може редагувати всі події'),
        ]


class EventActions:
    CREATED = 'created'
    UPDATED = 'updated'
    COMPLETED = 'completed'


class EventLog(models.Model):
    action = models.CharField(max_length=50, default=EventActions.CREATED, verbose_name='Дія')
    model = models.CharField(max_length=90, verbose_name='Модель')
    object_id = models.IntegerField(verbose_name='ID обʼєкту')

    def __str__(self):
        return f'{self.action}-{self.model}-{self.object_id}'


class Category(models.Model):
    name = models.CharField(max_length=100)
