from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .serializers import RegistrationSerializer, LoginSerializer

User = get_user_model()

class RegistrationView(APIView):
    """
    API endpoint for user registration.

    POST:
        Expects RegistrationSerializer fields.
        On success: creates user, returns auth token and user data.
        On failure: returns error messages from serializer.
    """
    permission_classes = []

    def post(self, request):
        """
        Create a new user and return token with user data.

        Returns:
            HTTP 201: User created, token and user info in response.
            HTTP 400: Validation errors.
        """
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
    """
    API endpoint for user authentication via email and password.

    POST:
        Expects LoginSerializer fields.
        On success: returns auth token and user data.
        On failure: returns error messages or invalid credentials.
    """
    permission_classes = []

    def post(self, request):
        """
        Authenticate user and return token.

        Returns:
            HTTP 200: Valid credentials, token and user info.
            HTTP 401: Invalid credentials.
            HTTP 400: Validation errors.
        """
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
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST) #hier war mal 401
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailCheckView(APIView):
    """
    API endpoint to check if an email is registered.

    GET:
        Requires authentication.
        Query param: email
        Returns user data if found, error if not.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Checks whether the specified email exists.

        Query Params:
            email (str): Email to check.
        Returns:
            200: User info if exists.
            400: Missing email param.
            404: Email not found.
        """
        email = request.query_params.get("email")
        if not email:
            return Response({"detail": "Email parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            return Response({
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname
            })
        except User.DoesNotExist:
            return Response({"detail": "Email not found."}, status=status.HTTP_404_NOT_FOUND)
