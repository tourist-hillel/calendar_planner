from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from events.models import Event
from categories.models import Category
from django.utils import timezone


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_time', 'end_time', 'category']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                # 'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
                }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                # 'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }),
        }

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # if self.instance and self.instance.id:
        #     self.fields['start_time'].widget.attrs.update({
        #         'min': self.instance.start_time.strftime('%Y-%m-%dT%H:%M'),
        #         'max': self.instance.start_time.strftime('%Y-%m-%dT%H:%M'),
        #         'type': 'datetime-local',
        #         'readonly': 'readonly'
        #     })
        #     if self.instance.end_time < timezone.now():
        #         self.fields['end_time'].widget.attrs.update({
        #             'min': self.instance.start_time.strftime('%Y-%m-%dT%H:%M'),
        #             'max': self.instance.end_time.strftime('%Y-%m-%dT%H:%M'),
        #             'type': 'datetime-local',
        #             'readonly': 'readonly'
        #         })

        
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not self.instance.id:
            if len(title) < 5:
                raise forms.ValidationError('Назва події повинна містити щонайменше 5 символів')
            
            if self.user and Event.objects.filter(user=self.user, title=title).exclude(id=self.instance.id).exists():
                raise forms.ValidationError('Подія з такою назвою вже існує')
        return title
    
    # def clean_start_time(self):
    #     start_time = self.cleaned_data.get('start_time')
    #     if not self.instance.id or self.instance.id and start_time != self.instance.start_time:
    #         if start_time < timezone.now():
    #             raise forms.ValidationError('Дата початку не може бути у минулому')
    #     return start_time

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError('Дата закінчення не може бути раніше дати початку')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        # if self.user:
        #     instance.user = self.user
        # if commit:
        #     instance.save()
        #     # instance.save_m2m()
        
        return instance
    


class EventSearchForm(forms.Form):
    query = forms.CharField(
        label='Пошук за назвою',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введіть назву події',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        label='Категорія',
        queryset=Category.objects.all(),
        required=False,
        empty_label='Усі категорії',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


EventFormSet = forms.formset_factory(EventForm, extra=2)