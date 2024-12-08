from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User, VIA_PHONE, VIA_EMAIL, VERIFICATION_CODE, DONE
from users.utility import email_or_phone_number, send_email_cod


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    auth_stats = serializers.CharField(read_only=True, required=False)
    auth_type = serializers.CharField(read_only=True, required=False)
    phone = serializers.CharField(read_only=True, required=False)
    email = serializers.CharField(read_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        self.fields['email_or_phone'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'auth_stats', 'auth_type', 'phone', 'email']

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        if user.auth_type == VIA_PHONE:
            code = user.create_verification_code(VIA_PHONE)
        elif user.auth_type == VIA_EMAIL:
            code = user.create_verification_code(VIA_EMAIL)
            send_email_cod(user.email, code)

        return user

    def validate(self, attrs):
        super(UserSerializer, self).validate(attrs)
        data = self.auth_validate(attrs)
        return data

    @staticmethod
    def auth_validate(attrs):
        user_input = str(attrs.get('email_or_phone'))
        input_user = email_or_phone_number(user_input)
        # print(input_user, user_input)
        if input_user == 'phone':
            data = {
                'phone': user_input,
                'auth_type': VIA_PHONE
            }
        elif input_user == 'email':
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL
            }
        else:
            data = {
                'status': False,
                'message': 'Email yoki telefon raqam kiriting!'
            }
            raise ValidationError(data)

        return data

    def validate_email_or_phone(self, values):
        values = values.lower()
        if User.objects.filter(email=values).exists():
            data = {
                'status': False,
                'message': 'Bunday emaildan avval foydalanilgan'
            }
            raise ValidationError(data)

        elif User.objects.filter(phone=values).exists():
            data = {
                'status': False,
                'message': 'Bunday telefon raqamdan foydalanilgan!'
            }
            raise ValidationError(data)

        return values

    def to_representation(self, instance):
        user = super(UserSerializer, self).to_representation(instance)
        user.update(instance.token())
        return user


class ConfSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4, write_only=True)


class UserChangeSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, write_only=True, required=True)
    last_name = serializers.CharField(max_length=30, write_only=True, required=True)
    username = serializers.CharField(max_length=30, write_only=True, required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, attrs):
        password = attrs.get('password', None)
        confirm_password = attrs.get('confirm_password', None)
        if password != confirm_password:
            data = {
                'status': False,
                'message': 'Parollar bir xil emas!'
            }
            raise ValidationError(data)
        if password:
            validate_password(password)
            validate_password(confirm_password)
        return attrs

    def validate_username(self, username):
        if len(username) < 5 or len(username) > 30:
            data = {
                'status': False,
                'message': 'Foydalanuvchi nomi 5 dan 30 gacha bo\'lishi kerak!'
            }
            raise ValidationError(data)
        return username

    def validate_first_name(self, first_name):
        if len(first_name) < 2 or len(first_name) > 30:
            data = {
                'status': False,
                'message': 'Foydalanuvchi ismi 2 dan 30 gacha bo\'lishi kerak!'
            }
            raise ValidationError(data)
        return first_name

    def validate_last_name(self, last_name):
        if len(last_name) < 2 or len(last_name) > 30:
            data = {
                'status': False,
                'message': 'Foydalanuvchi familiyasi 2 dan 30 gacha bo\'lishi kerak!'
            }
            raise ValidationError(data)
        return last_name

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.set_password(validated_data.get('password', instance.password))
        if instance.auth_type == VERIFICATION_CODE:
            instance.auth_type = DONE
        instance.save()
        return instance


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar']




