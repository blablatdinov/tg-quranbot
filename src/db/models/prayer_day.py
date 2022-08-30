from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import Date

from db.base import Base


class PrayerDay(Base):
    """День для намаза."""

    __tablename__ = 'prayer_days'

    date = Column(Date(), primary_key=True)
