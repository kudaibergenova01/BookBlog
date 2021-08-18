from rest_framework import serializers

from .models import MyUser
from .utils import send_activation_code


class RegisterSerializers(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'password_confirm')

    def validate(self, attrs):
        password = attrs.get('password')
        password_conf = attrs.pop('password_confirm')
        if password != password_conf:
            raise serializers.ValidationError('Passwords do not much')
        return attrs

    def create(self, validated_data):
        user = MyUser.objects.create_user(**validated_data)
        send_activation_code(user.email, user.activation_code, status='register')
        return user