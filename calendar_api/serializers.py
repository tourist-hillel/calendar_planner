from rest_framework import serializers
from django.contrib.auth import get_user_model
from events.models import Event
from categories.models import Category
from django.utils import timezone

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'cell_phone', 'date_of_birth', 'first_name', 'last_name', 'preffered_lang', 'full_name']
        read_only_fields = ['id', 'full_name']


class EventSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True), source='user', write_only=True
    )
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, allow_null=True
    )
    is_overdue = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_time', 'end_time',
            'created_at', 'is_completed', 'user_id', 'user', 'category', 'category_id',
            'is_overdue', 'duration'
        ]
        read_only_fields = ['id', 'created_at', 'is_overdue', 'duration', 'user']

    def get_is_overdue(self, obj):
        if not obj.is_completed and obj.end_time:
            return obj.end_time < timezone.now()
        return False
    
    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            hours = delta.total_seconds() // 3600
            minutes = (delta.total_seconds() % 3600) // 60
            return f'{int(hours)}год. {int(minutes)} хв'
        return None
    
    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError('Час закінчення задачі не може бути раніше за час початку')
        if end_time and end_time < timezone.now():
            raise serializers.ValidationError('Час закінчення не може бути у минулому')
        return attrs
    
    def create(self, validated_data):
        # validated_data['title'] = validated_data['title'] + "added from 'create()'"
        # validated_data['user'] = self.context['request'].user
        return super().create(validated_data)