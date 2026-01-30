from django.urls import path
from .views import (
    RegisterView, VerifyEmailView, LoginView,
    CategoryListView, EventListCreateView, 
    TicketListCreateView, BookTicketView, EventDetailView, TicketDetailView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifyEmailView.as_view(), name='verify'),
    path('login/', LoginView.as_view(), name='login'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('events/', EventListCreateView.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),

    path('tickets/', TicketListCreateView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<int:pk>/book/', BookTicketView.as_view(), name='book-ticket'),
]
