from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import String

from db.base import Base


class AdminMessage(Base):
    """Модель административного сообщения."""

    __tablename__ = 'admin_messages'

    key = Column(String(), primary_key=True)
    text = Column(String())
