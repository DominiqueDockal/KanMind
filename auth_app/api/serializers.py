from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates matching passwords and creates a new User with an auth token.
    """
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]

    def validate(self, attrs):
        """
        Checks that password and repeated_password match.

        Raises:
            ValidationError: If passwords do not match.
        """
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        """
        Removes repeated_password, creates the user and an auth token.

        Returns:
            User instance.
        """
        validated_data.pop("repeated_password")
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Expects email and password fields.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

