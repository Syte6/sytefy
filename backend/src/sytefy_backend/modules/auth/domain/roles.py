"""Yerleşik rol tanımları."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RoleDefinition:
    slug: str
    name: str
    description: str
    is_assignable: bool


BUILTIN_ROLES: tuple[RoleDefinition, ...] = (
    RoleDefinition(
        slug="owner",
        name="Sahip",
        description="Kurucu/Süper kullanıcı; tüm izinler.",
        is_assignable=False,
    ),
    RoleDefinition(
        slug="admin",
        name="Yönetici",
        description="Takım yönetimi, müşteri ve finans işlemleri dahil tüm modüller.",
        is_assignable=True,
    ),
    RoleDefinition(
        slug="staff",
        name="Danışman",
        description="Günlük müşteri ve randevu operasyonları.",
        is_assignable=True,
    ),
    RoleDefinition(
        slug="viewer",
        name="İzleyici",
        description="Salt-okunur raporlama ve kayıtlara erişim.",
        is_assignable=True,
    ),
)


__all__ = ["RoleDefinition", "BUILTIN_ROLES"]
