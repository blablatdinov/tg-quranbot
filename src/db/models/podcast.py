from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String

from db.base import Base


class Podcast(Base):
    __tablename__ = 'podcasts'

    podcast_id = Column(String(), primary_key=True)
    file_id = Column(String(), ForeignKey('files.file_id'))
