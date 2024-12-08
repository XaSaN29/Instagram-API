from django.urls import path
from users.views import UserSignUpView, UserConfirmationView, NewCode, UserChangeView, UserPhoneView, UserLoginAPIView


urlpatterns = [
    path('user/', UserSignUpView.as_view(), name='user-create'),
    path('user-login/', UserLoginAPIView.as_view(), name='user-login'),
    path('code/', UserConfirmationView.as_view(), name='code'),
    path('new_code/', NewCode.as_view(), name='new_code'),
    path('user_change/', UserChangeView.as_view(), name='user_change'),
]
