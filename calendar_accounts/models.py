import logging
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta, timezone as tz

logger = logging.getLogger(__name__)

LOCKOUT_DEFAULT = settings.LOCKOUT_DURATION_MINUTES
MAX_LOGIN_ATTEMPTS = settings.MAX_FAILED_ATTEMPTS

SUPPORTED_LANGUAGES = [
    ('uk', 'Ukrainian'),
    ('en', 'English')
]


class CalendarUserManager(BaseUserManager):
    def create_user(self, cell_phone, email, password=None, **extra_fields):
        if not cell_phone:
            raise ValueError('Cell phone is required')
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(cell_phone=cell_phone, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, cell_phone, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True!!!')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True!!!')
        return self.create_user(cell_phone, email, password, **extra_fields)


class CalendarUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    cell_phone = models.CharField(max_length=10, unique=True, verbose_name='Cell phone')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Date of birth')
    first_name = models.CharField(max_length=30, blank=True, verbose_name='First name')
    last_name = models.CharField(max_length=50, blank=True, verbose_name='Last name')
    profile_image = models.ImageField(
        upload_to='profile_images/', null=True, blank=True, verbose_name='Profile picture'
    )
    is_active = models.BooleanField(default=True, verbose_name='Is active')
    is_staff = models.BooleanField(default=False, verbose_name='Is staff')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Date of account creation')
    preffered_lang = models.CharField(
        max_length=10, choices=SUPPORTED_LANGUAGES, default='uk', verbose_name='Preferred language'
    )
    password_changed_at = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)

    objects = CalendarUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'cell_phone'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Calendar user'
        verbose_name_plural = 'Calendar users'
        permissions = [
            ('can_set_user_permissions', 'Може додавати дозволи користувачеві'),
            ('can_see_user_permissions', 'Може переглядати список дозволів користувача')
        ]

    def __str__(self):
        return self.email

    def set_password(self, raw_password: str | None) -> None:
        super().set_password(raw_password)
        self.password_changed_at = datetime.now()
        self.failed_login_attempts = 0
        self.account_locked_until = None

    def _unlock_account(self):
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save()

    @property
    def is_account_locked(self):
        logger.info(f'processing is locked check for{self.cell_phone}')
        logger.info(f'account_locked_until: {self.account_locked_until}')
        now_date = datetime.now().replace(tzinfo=tz.utc)
        if self.account_locked_until and now_date < self.account_locked_until:
            logger.info('still locked')
            return True
        logger.info('should be unlocked')
        return False

    def _lock_account(self, lock_time_minutes=LOCKOUT_DEFAULT) -> None:
        if not self.is_account_locked:
            lock_time = datetime.now().replace(tzinfo=tz.utc) + timedelta(minutes=lock_time_minutes)
            self.account_locked_until = lock_time
            self.save()

    @classmethod
    def process_failed_login_attempt(cls, user, **kwargs):
        max_attempts = kwargs.get('max_attempts', MAX_LOGIN_ATTEMPTS)
        lock_time = 3 if user.is_superuser else kwargs.get('lock_time', LOCKOUT_DEFAULT)
        user.failed_login_attempts += 1
        user.save(update_fields=['failed_login_attempts'])
        if user.failed_login_attempts >= max_attempts:
            user._lock_account(lock_time_minutes=lock_time)

    @classmethod
    def process_success_login_attempt(cls, user, **kwargs):
        user._unlock_account()

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()
