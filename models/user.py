from .base import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    name = Column(String)
    age = Column(Integer)
