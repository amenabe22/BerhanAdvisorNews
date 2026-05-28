"""PostgreSQL enum column helpers (types created in migration 001)."""

from enum import Enum as PyEnum

from sqlalchemy import Enum as SAEnum


def pg_enum(enum_cls: type[PyEnum], name: str) -> SAEnum:
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=True,
        create_constraint=True,
        values_callable=lambda obj: [e.value for e in obj],
        validate_strings=True,
        create_type=False,
    )
