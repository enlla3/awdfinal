from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser
from .serializers import CustomUserSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    # Define the queryset to retrieve all CustomUser objects
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # Set the permission to allow only authenticated users
    permission_classes = [IsAuthenticated]
