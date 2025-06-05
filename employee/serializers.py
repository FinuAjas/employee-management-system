from rest_framework import serializers
from .models import CustomUser, FormField, Employee
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that adds additional user claims to JWT tokens.
    Inherits from TokenObtainPairSerializer to include default token claims.
    """
    
    @classmethod
    def get_token(cls, user):
        """
        Create JWT token with custom claims.
        
        Args:
            user: The user instance for which the token is being created.
            
        Returns:
            Token: The JWT token with added custom claims including email,
                  first name, and last name.
        """
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles validation of registration data and user creation.
    """
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """
        Validate that the two password fields match.
        
        Args:
            attrs: Dictionary of serializer field values.
            
        Returns:
            dict: Validated attributes if passwords match.
            
        Raises:
            ValidationError: If passwords don't match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user instance.
        
        Args:
            validated_data: Validated registration data.
            
        Returns:
            CustomUser: The newly created user instance.
        """
        user = CustomUser.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    Validates old password and ensures new password meets requirements.
    """
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    Validates email uniqueness and required fields.
    """
    
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'address')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """
        Validate that the email is unique (excluding current user).
        
        Args:
            value: Email value to validate.
            
        Returns:
            str: Validated email if unique.
            
        Raises:
            ValidationError: If email is already in use by another user.
        """
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        return value

class FormFieldSerializer(serializers.ModelSerializer):
    """
    Serializer for FormField model.
    Handles serialization/deserialization of custom form fields.
    """
    
    class Meta:
        model = FormField
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')

class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.
    Includes nested user serializer for user-related fields.
    """
    
    user = UpdateUserSerializer()

    class Meta:
        model = Employee
        fields = '__all__'

    def update(self, instance, validated_data):
        """
        Update employee instance including nested user data.
        
        Args:
            instance: Employee instance to update.
            validated_data: Validated data containing employee and user fields.
            
        Returns:
            Employee: The updated employee instance.
        """
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UpdateUserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
        
        instance.fields = validated_data.get('fields', instance.fields)
        instance.save()
        return instance