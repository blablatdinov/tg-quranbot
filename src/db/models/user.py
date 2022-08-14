from sqlalchemy.sql import expression
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, Integer, String

from db.base import Base


class User(Base):
    __tablename__ = 'users'

    chat_id = Column(Integer(), primary_key=True)
    is_active = Column(Boolean(), server_default=expression.true(), nullable=False)
    comment = Column(String())
    day = Column(Integer(), default=2)
    city_id = Column(String(), ForeignKey('cities.city_id'))
    referrer_id = Column(Integer(), ForeignKey('users.chat_id'))
