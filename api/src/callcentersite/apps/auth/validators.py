"""Validadores relacionados con contraseñas y autenticación."""

from __future__ import annotations

import re
from typing import Optional

from django.core.exceptions import ValidationError


def validate_password_complexity(password: str, user: Optional[object] = None) -> None:
    """Valida reglas básicas de complejidad de contraseñas."""

    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres")
    if len(password) > 100:
        raise ValidationError("La contraseña no puede exceder 100 caracteres")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("La contraseña debe incluir al menos una mayúscula")
    if not re.search(r"[a-z]", password):
        raise ValidationError("La contraseña debe incluir al menos una minúscula")
    if not re.search(r"\d", password):
        raise ValidationError("La contraseña debe incluir al menos un dígito")
    if not re.search(r"[!@#$%^&*(),.?\":{}|\[\]\\/;'`~<>+-]", password):
        raise ValidationError("La contraseña debe incluir al menos un carácter especial")

    username = getattr(user, "username", "") if user else ""
    if username and username.lower() in password.lower():
        raise ValidationError("La contraseña no debe contener el username")
