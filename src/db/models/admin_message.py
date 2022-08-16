from db.base import Base

from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import String


class AdminMessage(Base):

    __tablename__ = 'admin_messages'

    key = Column(String(), primary_key=True)
    text = Column(String())
