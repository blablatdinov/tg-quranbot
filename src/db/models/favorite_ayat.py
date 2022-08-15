from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Integer

from db.base import Base


class FavoriteAyat(Base):
    """Модель избранных аятов."""

    __tablename__ = 'favorite_ayats'

    ayat_id = Column(Integer(), ForeignKey('ayats.ayat_id'))
    user_id = Column(Integer(), ForeignKey('users.chat_id'))

    __table_args__ = PrimaryKeyConstraint(ayat_id, user_id)
