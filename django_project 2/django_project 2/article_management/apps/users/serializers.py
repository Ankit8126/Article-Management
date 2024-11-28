# apps/users/serializers.py
from rest_framework import serializers
from .models import User  # or your actual user model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Or specify the fields you want to serialize
