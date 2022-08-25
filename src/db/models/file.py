from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, String

from db.base import Base


class File(Base):  # noqa: WPS110
    """Модель файла."""

    __tablename__ = 'files'

    file_id = Column(String(), primary_key=True)
    telegram_file_id = Column(String(), nullable=True)
    link = Column(String(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
