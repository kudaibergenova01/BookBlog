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


class CreateNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    activation_code = serializers.CharField(max_length=25, required=True)
    password = serializers.CharField(min_length=8, required=True)
    password_confirm = serializers.CharField(min_length=8, required=True)

    def validate_email(self, email):
        if not MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return email

    def validate_activation_code(self, act_code):
        if not MyUser.objects.filter(activation_code=act_code, is_active=False).exists():
            raise serializers.ValidationError('Неверный код активации')
        return act_code

    def validate(self, attrs):
        password = attrs.get('password')
        password_conf = attrs.pop('password_confirm')
        if password != password_conf:
            raise serializers.ValidationError('Passwords do not much')
        return attrs

    def save(self, **kwargs):
        data = self.validated_data
        email = data.get('email')
        activation_code = data.get('activation_code')
        password = data.get('password')
        try:
            user = MyUser.objects.get(email=email,
                                      activation_code=activation_code,
                                      is_active=False)
        except MyUser.DoesNotExist:
            raise serializers.ValidationError('Пользователь не найден')

        user.is_active = True
        user.activation_code = ''
        user.set_password(password)
        user.save()
        return user