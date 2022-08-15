from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from db.base import Base


class Ayat(Base):
    """Модель аята."""

    __tablename__ = 'ayats'

    ayat_id = Column(Integer(), primary_key=True)
    public_id = Column(String(), nullable=False)
    sura_id = Column(Integer(), ForeignKey('suras.sura_id'), nullable=False)
    day = Column(Integer())
    ayat_number = Column(String(length=10), nullable=False)
    content = Column(String(), nullable=False)
    arab_text = Column(String(), nullable=False)
    transliteration = Column(String(), nullable=False)
