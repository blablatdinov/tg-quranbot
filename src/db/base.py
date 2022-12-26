from databases import Database
from sqlalchemy.orm import declarative_base

from settings import settings

Base = declarative_base()

database = Database(settings.DATABASE_URL)
