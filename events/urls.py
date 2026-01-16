from django.urls import path
from events.views import (
    events_list,
    create_event,
    edit_event,
    create_event_bulk,
    EventListView,
    EventUpdateView,
    CreateEventView,
    chat_index,
    upload_files_to_s3,
    files_list_s3
)

urlpatterns = [
    path('', events_list, name='event_list'),
    path('cbv_list/', EventListView.as_view(), name='event_list_cbv'),
    path('create/', create_event, name='create_event'),
    path('create_cbv/', CreateEventView.as_view(), name='crate_cbv'),
    path('create_bulk/', create_event_bulk, name='create_event_bulk'),
    path('edit/<int:event_id>', edit_event, name='edit_event'),
    path('edit_cbv/<int:event_id>', EventUpdateView.as_view(), name='edit_event_cbv'),
    path('room/<str:room_name>/', chat_index, name='chat'),
    path('upload_to_s3/', upload_files_to_s3, name='upload_to_s3'),
    path('files-list-s3/', files_list_s3, name='files_list_s3'),
]