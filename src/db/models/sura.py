from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String

from db.base import Base


class Sura(Base):
    __tablename__ = 'suras'

    sura_id = Column(Integer(), primary_key=True)
    link = Column(String())
