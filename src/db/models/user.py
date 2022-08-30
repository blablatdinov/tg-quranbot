from sqlalchemy.sql import expression
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, Integer, String

from db.base import Base


class User(Base):
    """Модель пользователя."""

    __tablename__ = 'users'

    chat_id = Column(BigInteger(), primary_key=True, autoincrement=False)
    is_active = Column(Boolean(), server_default=expression.true(), nullable=False)
    comment = Column(String())
    day = Column(Integer(), default=2)
    city_id = Column(String(), ForeignKey('cities.city_id'))
    referrer_id = Column(Integer(), ForeignKey('users.chat_id'))
    legacy_id = Column(Integer(), nullable=True)
