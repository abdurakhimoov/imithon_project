from django.contrib import admin
from .models import User, Category, Event, Ticket, Booking

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'is_verified']
    search_fields = ['email']
    list_filter = ['is_verified']


@admin.register(Category)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Event)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'category', 'title', 'created_at']
    search_fields = ['owner', 'category', 'title']
    list_filter = ['category']  


@admin.register(Ticket)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'price', 'quantity']
    search_fields = ['event']


@admin.register(Booking)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'ticket', 'created_at']
    search_fields = ['user', 'ticket']