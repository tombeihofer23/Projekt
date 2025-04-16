"""Basisklasse für Entity-Klassen."""

from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:

    class MappedAsDataclass:
        """
        Mixin class ohne die Directiven von PEP 681.
        https://peps.python.org/pep-0681
        https://github.com/python/mypy/issues/13856
        https://github.com/python/mypy/issues/14868
        https://docs.sqlalchemy.org/en/20/orm/dataclasses.html
        """

        def __init__(self, *args: Any, **kw: Any) -> None:
            """Mixin class ohne die Directiven von PEP 681."""

else:
    from sqlalchemy.orm import MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    """Basisklasse für Entity-Klassen als dataclass"""
