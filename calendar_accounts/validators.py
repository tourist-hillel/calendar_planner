import logging
from datetime import datetime, timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

SPECIAL_CHARS = '!@#$%^&*()_+{}|:;<>?'


class SpecialCharsValidator:
    def __init__(self, special_chars=SPECIAL_CHARS, min_special_chars=1) -> None:
        self.special_chars = special_chars
        self.min_special_chars = min_special_chars

    def validate(self, password, user=None):
        special_count = sum(1 for char in password if char in self.special_chars)

        if special_count < self.min_special_chars:
            raise ValidationError(
                _(f'Пароль повинен містити мінімум {self.min_special_chars} спеціальних символів'
                  f' з наступних: {self.special_chars}'),
                code='password_no_special'
            )

    def get_help_text(self):
        return _(f'Пароль повинен містити мінімум {self.min_special_chars} спеціальних символів'
                 f'({self.special_chars})')


class UppercaseLowercaseValidator:
    def __init__(
            self,
            require_uppercase=True,
            require_lowercase=True,
            min_uppercase=1,
            min_lowercase=1
    ):
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase

    def validate(self, password, user=None):
        if self.require_uppercase:
            uppercase_count = sum(1 for char in password if char.isupper())
            if uppercase_count < self.min_uppercase:
                raise ValidationError(
                    _(f'Пароль повинен містити мінімум {self.min_uppercase} символів верхнього регістру'),
                    code='password_no_uppercase'
                )
        if self.require_lowercase:
            lowercase_count = sum(1 for char in password if char.islower())
            if lowercase_count < self.min_uppercase:
                raise ValidationError(
                    _(f'Пароль повинен містити мінімум {self.min_lowercase} символів нижнього регістру'),
                    code='password_no_lowercase'
                )

    def get_help_text(self):
        help_texts = []
        if self.require_lowercase:
            help_texts.append(f'{self.min_lowercase} нижнього регістру')
        if self.require_uppercase:
            help_texts.append(f'{self.min_uppercase} верхнього регістру')

        return _("Ваш пароль повинен містити мінімум " + " та ".join(help_texts) + ".")


class RepeatingCharacterValidator:
    def __init__(self, max_repeating=2):
        self.max_repeating = max_repeating

    def validate(self, password, user=None):
        count = 1
        prev_char = ''
        for char in password:
            if char == prev_char:
                count += 1
                if count > self.max_repeating:
                    raise ValidationError(
                        _(f'Пароль не повинен містити більше {self.max_repeating} однакових символів підряд'),
                        code='password_to_many_repeating'
                    )
            else:
                count = 1
                prev_char = char

    def get_help_text(self):
        return _(f'Пароль не повинен містити більше {self.max_repeating} однакових символів підряд')


class ExpirationWarningValidator:
    def __init__(self, expiration_days=90, warning_days=14):
        self.expiration_days = expiration_days
        self.warning_days = warning_days

    def validate(self, password, user=None):
        pass

    def get_help_text(self):
        return _(f'Пароль має термін дії {self.expiration_days} днів.'
                 f'Ви отримаєте попередження за {self.warning_days} днів до закінчення терміну.')

    def check_expiration(self, user):
        if hasattr(user, 'password_changed_at'):
            logger.info(f'Check expiration for User {user}, password_changed_at: {user.password_changed_at}')
            if user.password_changed_at is None:
                return {'expired': True, 'days_overdue': 0}
            days_since_change = (datetime.now().replace(tzinfo=timezone.utc) - user.password_changed_at).days

            if days_since_change >= self.expiration_days:
                return {'expired': True, 'days_overdue': days_since_change - self.expiration_days}
            elif days_since_change >= (self.expiration_days - self.warning_days):
                return {'warning': True, 'days_remaining': self.expiration_days - days_since_change}
            return {'ok': True}
