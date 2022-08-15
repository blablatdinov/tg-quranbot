from db.base import Base

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Date, Integer


class PrayerAtUserGroup(Base):

    __tablename__ = 'prayers_at_user_groups'

    prayers_at_user_group_id = Column(String(), primary_key=True)


class PrayerAtUser(Base):
    """Модель времени намаза у пользователя."""

    __tablename__ = 'prayers_at_user'

    prayer_at_user_id = Column(String(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.chat_id'), nullable=False)
    prayer_id = Column(String(), ForeignKey('prayers.prayer_id'))
    day_id = Column(Date(), ForeignKey('prayer_days.date'))
    prayer_group_id = Column(String(), ForeignKey('prayers_at_user_groups.prayers_at_user_group_id'))
