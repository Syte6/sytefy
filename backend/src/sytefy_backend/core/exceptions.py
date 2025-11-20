"""Domain/application level exception hierarchy."""

from __future__ import annotations

from typing import Any, Dict


class ApplicationError(Exception):
    status_code = 400
    detail = "Beklenmeyen bir hata oluştu."

    def to_dict(self) -> Dict[str, Any]:
        return {"error": self.__class__.__name__, "detail": self.detail}


class NotFoundError(ApplicationError):
    status_code = 404
    detail = "Kayıt bulunamadı."


class AuthorizationError(ApplicationError):
    status_code = 403
    detail = "Bu işlem için yetkiniz bulunmuyor."


class ValidationError(ApplicationError):
    status_code = 422
    detail = "Gönderilen veriler doğrulama kurallarına uymuyor."
