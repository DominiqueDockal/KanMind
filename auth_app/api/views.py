from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, LoginSerializer


User = get_user_model()

class RegistrationView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(request, email=email, password=password)
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "token": token.key,
                    "fullname": user.fullname,
                    "email": user.email,
                    "user_id": user.id,
                }, status=status.HTTP_200_OK)
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
