from typing import Any
import logging
from django.shortcuts import redirect
from django.urls import reverse
from calendar_accounts.validators import ExpirationWarningValidator


logger = logging.getLogger(__name__)


class PasswordExpirationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.validator = ExpirationWarningValidator()

    def __call__(self, request, **kwargs) -> Any:
        logger.info('Expiration middleware span')
        if request.user.is_authenticated:
            logger.info(f'Start processing user - {request.user}')
            status = self.validator.check_expiration(request.user) or dict()
            logger.info(f'Revieved status: {status}')

            if status.get('expired'):
                logger.info(f'[request.path] {request.path}')
                if not request.path.startswith('/reset-password'):
                    return redirect('reset_password')
            elif status.get('warning'):
                from django.contrib import messages
                messages.warning(
                    request,
                    f'Ваш пароль закінчується через {status.get("days_remaining")} днів. Будь ласка змініть його'
                )
        response = self.get_response(request)
        return response
