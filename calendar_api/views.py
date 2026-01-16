import jwt
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from events.models import Event
from categories.models import Category
from calendar_api.serializers import EventSerializer, CategorySerializer, UserSerializer
from calendar_api.utils import create_access_token, create_refresh_token

User = get_user_model()



class EventViewSet(viewsets.ModelViewSet):
    # authentication_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    serializer_class = EventSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['start_time', 'end_time', 'created_at']
    ordering = ['-start_time']
    # queryset = Event.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        return Event.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        event = self.get_object()
        # if event.user != request.user:
        #     return Response({'detail': 'Ви не можете завершувати чужі події'}, status=status.HTTP_403_FORBIDDEN)
        event.is_completed = True
        event.save()

        return Response(EventSerializer(event).data)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        user = authenticate(
           username =  request.data.get('cell_phone'),
           password =  request.data.get('password')
        )

        if not user:
            return Response({'error': 'Неправильні креди'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'access': create_access_token(user),
            'refresh': create_refresh_token(user)
        })


class RefreshView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        token = request.data.get('refresh')
        if not token:
            return Response({'error': 'Рефреш токен обовʼязковий'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            if payload.get('token_type') != 'refresh':
                raise AuthenticationFailed('Невірний тип токену')
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Токен протерміновано'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Невалідний токен'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=payload['user_id'], is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'Користувача не знайдено'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'access': create_access_token(user)
        })
