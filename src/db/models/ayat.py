from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from db.base import Base


class Ayat(Base):
    __tablename__ = 'ayats'

    ayat_id = Column(Integer(), primary_key=True, autoincrement=True)
    public_id = Column(String())
    sura_id = Column(Integer(), ForeignKey('suras.sura_id'))
    day = Column(Integer())
    ayat_number = Column(String(length=10))
    content = Column(String())
    arab_text = Column(String())
    transliteration = Column(String())
