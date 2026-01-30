from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from .serializers import RegisterSerializer, VerifyEmailSerializer, LoginSerializer, CategorySerializer, EventSerializer, TicketSerializer, BookingSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Category, Event, Ticket, Booking
from .permission import IsOwnerOrReadOnly, IsTicketOwnerOrReadOnly


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        code = user.generate_code()

        print(f"DEBUG: Verification code for {user.email}: {code}")
        
        send_mail(
            'Tasdiqlash kodi',
            f'Sizning kodingiz: {code}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        return Response({
            "message": "Ro'yxatdan o'tdingiz. Tasdiqlash kodi emailingizga yuborildi.",
            "email": user.email
        }, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    serializer_class = VerifyEmailSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            try:
                user = User.objects.get(email=email)
                
                if user.verification_code == code:
                    user.is_verified = True
                    user.verification_code = None
                    user.save()
                    return Response({"message": "Email tasdiqlandi!"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Kod noto'g'ri!"}, status=status.HTTP_400_BAD_REQUEST)
            
            except User.DoesNotExist:
                return Response({"error": "Foydalanuvchi topilmadi!"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username
        }, status=status.HTTP_200_OK)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class= CategorySerializer
    permission_classes = [permissions.AllowAny]


class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class TicketListCreateView(generics.ListCreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()


class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsTicketOwnerOrReadOnly]


class BookTicketView(APIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not request.user.is_verified:
            return Response({
                "error": "Chipta sotib olish uchun avval profilingizni SMS orqali tasdiqlang!"
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            ticket = Ticket.objects.get(pk=pk)

            if ticket.quantity > 0:
                ticket.quantity -= 1
                ticket.save()
                
                booking = Booking.objects.create(user=request.user, ticket=ticket)

                confirm_msg = f"Siz '{ticket.event.title}' tadbiriga chipta bron qildingiz!"
                print(f"\n[BRON TASDIQLANDI]: {confirm_msg}\n")
                
                return Response({
                    "message": "Muvaffaqiyatli bron qilindi!",
                    "booking_id": booking.id
                }, status=status.HTTP_201_CREATED)
            
            return Response({"error": "Chiptalar tugagan!"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Ticket.DoesNotExist:
            return Response({"error": "Chipta topilmadi!"}, status=status.HTTP_404_NOT_FOUND)

class MyBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)