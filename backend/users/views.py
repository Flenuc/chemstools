from django.shortcuts import render

from rest_framework import generics, permissions
from rest_framework.throttling import AnonRateThrottle
from .models import CustomUser
from .serializers import UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    throttle_classes = [AnonRateThrottle] # Aplicar throttling anónimo
    throttle_scope = 'auth' # Usar el scope 'auth' que definimos

# This view allows users to retrieve their own profile information.
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    
# Nota: Para la vista de login (TokenObtainPairView), la sobreescribiríamos
# en una clase propia para añadir el throttle_scope. Por ahora, el límite
# global de 'anon' ya le aplica una protección básica.
