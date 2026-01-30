from rest_framework import serializers
from .models import User, Category, Event, Ticket, Booking
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if user and user.is_active:
            if not user.is_verified:
                raise serializers.ValidationError("Email hali tasdiqlanmagan!")
            return user
        raise serializers.ValidationError("Email yoki parol xato!")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = Event
        fields = ['id', 'owner', 'category', 'title', 'description', 'date', 'location']


class TicketSerializer(serializers.ModelSerializer):
    event_title = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = Ticket
        fields = ['id', 'event', 'event_title', 'price', 'quantity']

    def validate_event(self, value):
        user = self.context['request'].user
        if value.owner != user:
            raise serializers.ValidationError("Siz faqat o'zingiz yaratgan tadbirga chipta qo'sha olasiz!")
        return value


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    event_title = serializers.ReadOnlyField(source='ticket.event.title')
    ticket_price = serializers.ReadOnlyField(source='ticket.price')

    class Meta:
        model = Booking
        fields = ['id', 'user', 'ticket', 'event_title', 'ticket_price', 'created_at']
        read_only_fields = ['user', 'created_at']