import datetime
import random
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

ADMIN = 'admin'
USER = 'user'
MANAGER = 'manager'

VIA_PHONE = 'via_phone'
VIA_EMAIL = 'via_email'

NEW = 'new'
VERIFICATION_CODE = 'verification_code'
DONE = 'done'
PHOTO_STEP = 'photo_step'


class BaseCreatedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseCreatedModel):
    USER_STATUS = (
        (ADMIN, ADMIN),
        (USER, USER),
        (MANAGER, MANAGER)
    )

    AUTH_TYPE = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )

    AUTH_STATUS = (
        (PHOTO_STEP, PHOTO_STEP),
        (NEW, NEW),
        (DONE, DONE),
        (VERIFICATION_CODE, VERIFICATION_CODE)
    )

    phone = models.CharField(max_length=100, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(blank=True, null=True, upload_to='images/user/')
    user_status = models.CharField(max_length=255, choices=USER_STATUS, default=USER)
    auth_stats = models.CharField(max_length=255, choices=AUTH_STATUS, default=NEW)
    auth_type = models.CharField(max_length=255, choices=AUTH_TYPE)

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def create_verification_code(self, verification_type):
        code = "".join([str(random.randint(1, 9)) for _ in range(4)])
        UserConfirmation.objects.create(
            code=code,
            user_id=self.id,
            verification_type=verification_type
        )

        return code

    def check_username(self):
        if not self.username:
            temp_username = f'instagram-{uuid.uuid4().__str__().split("-")[-1]}'
            self.username = temp_username
            while User.objects.filter(username=self.username).exists():
                self.username = f'instagram-{uuid.uuid4().__str__().split("-")[-1]}'

    def check_pass(self):
        if not self.password:
            temp_password = f'{uuid.uuid4().__str__().split("-")[-1]}'
            self.password = temp_password
            # print(self.password)

    def hash_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
            # print(self.password)

    def check_email(self):
        if self.email:
            self.email = self.email.lower()

    def token(self):
        access = RefreshToken.for_user(self)
        data = {
            'access_token': str(access.access_token),
            'refresh_token': str(access)
        }
        return data

    def clean(self):
        self.check_username()
        self.check_pass()
        self.check_email()
        self.hash_password()

    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)


class UserConfirmation(BaseCreatedModel):
    AUTH_STATUS = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )

    code = models.IntegerField()
    expire_time = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code')
    is_confirmed = models.BooleanField(default=False)
    verification_type = models.CharField(max_length=255, choices=AUTH_STATUS)

    def save(self, *args, **kwargs):
        if self.verification_type == VIA_PHONE:
            self.expire_time = datetime.datetime.now() + datetime.timedelta(minutes=3)
        #                      
        else:
            self.expire_time = datetime.datetime.now() + datetime.timedelta(minutes=5)

        super(UserConfirmation, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.code}'






