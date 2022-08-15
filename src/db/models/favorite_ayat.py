from db.base import Base

from sqlalchemy.schema import ForeignKey, Column, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Integer


class FavoriteAyat(Base):

    __tablename__ = 'favorite_ayats'

    ayat_id = Column(Integer(), ForeignKey('ayats.ayat_id'))
    user_id = Column(Integer(), ForeignKey('users.chat_id'))

    __table_args = PrimaryKeyConstraint(ayat_id, user_id)
