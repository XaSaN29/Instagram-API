from datetime import datetime

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, UpdateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users.models import User, NEW, VERIFICATION_CODE, UserConfirmation, VIA_EMAIL, VIA_PHONE
from users.serializers import UserSerializer, ConfSerializer, UserChangeSerializer, UserPhotoSerializer, LoginSerializer
from users.utility import send_email_cod


class UserSignUpView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserConfirmationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ConfSerializer
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ConfSerializer(data=request.data)
        if serializer.is_valid():
            self.verify_codee(user, serializer.validated_data.get("code"))
            data = {
                'status': 'Success',
                'message': f'Confirmation code {serializer.validated_data["code"]}',
                'access_token': user.token()['access_token'],
                'refresh_token': user.token()['refresh_token']
            }
        else:
            data = {
                'status': 'Fail',
                'message': serializer.errors
            }
        return Response(data)

    @staticmethod
    def verify_codee(user, code):
        verification = user.code.filter(
            code=code,
            is_confirmed=False,
            expire_time__gte=datetime.now()
        )
        if not verification.exists():
            data = {
                'status': 'Fail',
                'message': 'Code xato yokida eskirgan'
            }
            raise ValidationError(data)
        # print(verification)
        verification.update(is_confirmed=True)
        if user.auth_stats == NEW:
            user.auth_stats = VERIFICATION_CODE
            user.save()
        return True


class NewCode(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        self.check_validation_code(user)
        if user.auth_type == VIA_PHONE:
            code = user.create_verification_code(VIA_PHONE)
        elif user.auth_type == VIA_EMAIL:
            code = user.create_verification_code(VIA_EMAIL)
            send_email_cod(user.email, code)
        else:
            data = {
                'status': 'Fail',
                'message': 'Auth type not found'
            }
            raise ValidationError(data)
        return Response(
            {
                'status': 'Success',
                'message': 'Code yuborildi'
            }
        )

    @staticmethod
    def check_validation_code(user):
        verification = user.code.filter(
            is_confirmed=False,
            expire_time__gte=datetime.now()
        )
        if verification:
            data = {
                'message': 'Code xali yaroqli'
            }
            raise ValidationError(data)
        return user


class UserChangeView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch', 'put']

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        super(UserChangeView, self).update(request, *args, **kwargs)
        data = {
            'status': 'Success',
            'message': 'User updated successfully',
            'user_stats': self.request.user.auth_stats
        }
        return Response(data)


class UserPhoneView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserLoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=LoginSerializer
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            return Response({
                'access_token': user.token()['access_token'],
                'refresh_token': user.token()['refresh_token']
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




















