import logging
from django.db.models.query import QuerySet
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from botocore.exceptions import ClientError
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, FormView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from events.models import Event
from events.forms import EventForm, EventSearchForm, EventFormSet
from events.signals import custom_signal
from events.mixins import QueryFilterMixin, CategoryFilterMixin, OwnerRequiredMixin
from events.tasks import log_new_event
from calendar_accounts.forms import CalendarUserForm
from events.boto_client import get_s3_client, FILE_BUCKET_NAME

User = get_user_model()
logger = logging.getLogger(__name__)

@login_required
@permission_required('events.can_see_all_events', raise_exception=True)
def events_list(request):
    logger.info(f'User {request.user.email} accessed events page')
    try:
        search_form = EventSearchForm(request.GET or None)
        events = Event.objects.filter(user=request.user)
        logger.debug(f'User {request.user.email} viewing own events: {events.count()}')
        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            category = search_form.cleaned_data.get('category')

            if query:
                events = events.filter(title__icontains=query)
                logger.info(f'User {request.user.email} apply query: {query}')
            if category:
                events = events.filter(category=category)
                logger.info(f'User {request.user.email} apply category filter: {category}')
            logger.debug(f'User {request.user.email} viewing own events after applying filters: {events.count()}')
        return render(request, 'event_list.html', {'events': events, 'search_form': search_form})
    except Exception as e:
        logger.error(f'Error in "events_list" view: {str(e)}', exc_info=True)
        raise


class EventListView(PermissionRequiredMixin, QueryFilterMixin, ListView):
    model = Event
    template_name = 'event_list.html'
    context_object_name = 'events'
    permission_required = 'events.can_see_all_events'
    raise_exception = True
    query_field = 'title__icontains'
    query_param = 'query'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = EventSearchForm(self.request.GET or None)
        return context

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            log_new_event.delay(1234)
            custom_signal.send(sender=User, action='user_created_event', user=request.user)
            return redirect('event_list')
    else:
        form = EventForm(user=request.user)
    return render(request, 'event_form.html', {'form': form})

class CreateEventView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'event_form.html'
    success_url = reverse_lazy('event_list')

    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.user = self.request.user
        return super().form_valid(form)

@login_required
def create_event_bulk(request):
    if request.method == 'POST':
        formset = EventFormSet(request.POST, form_kwargs={'user': request.user})
        if formset.is_valid():
            # formset.save() - For Model Formset
            for form in formset:
                form.save()
            return redirect('event_list')
    else:
        formset = EventFormSet(form_kwargs={'user': request.user})
    return render(request, 'event_formset.html', {'formset': formset})

@login_required
@permission_required('events.can_edit_all_events', raise_exception=True)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event, user=request.user)
    return render(request, 'event_form.html', {'form': form})


class EventUpdateView(OwnerRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'event_form.html'
    success_url = reverse_lazy('event_list')
    pk_url_kwarg = 'event_id'

    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

@login_required
def chat_index(request, room_name):
    return render(request, 'chat/index.html', {'room_name': room_name})


def register(request):
    if request.method == 'POST':
        form = CalendarUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat', room_name='start_room')
    else:
        form = CalendarUserForm()

    return render(request, 'registration/register.html', {'form': form})


def upload_files_to_s3(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        default_storage.save(file.name, ContentFile(file.read()))
    return redirect('files_list_s3')

def files_list_s3(request):
    s3_client = get_s3_client()
    files = []
    errors = []
    continuation_token = None

    try:
        while True:
            params = {'Bucket': FILE_BUCKET_NAME}
            if continuation_token:
                params['ContinuationToken'] = continuation_token
            
            response = s3_client.list_objects_v2(**params)
            for file in response.get('Contents', []):
                file_name = file['Key']
                try:
                    file_params = params.copy()
                    file_params['Key'] = file_name
                    presigned_file_url = s3_client.generate_presigned_url(
                        'get_object',
                        Params=file_params,
                        ExpiresIn=30
                    )
                    files.append({
                        'file_name': file_name,
                        'file_url': presigned_file_url,
                        'size': file['Size'],
                        'last_modified': file['LastModified']
                    })
                except ClientError as e:
                    errors.append(e)
            if response.get('isTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break
    except ClientError as e:
        errors.append(e)

    return render(request, 's3_files_list.html', {'files': files, 'errors': errors})
