from db.base import Base

from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import Date


class PrayerDay(Base):

    __tablename__ = 'prayer_days'

    date = Column(Date(), primary_key=True)
