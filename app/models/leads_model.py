from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime

from dataclasses import dataclass

from datetime import datetime as dt

from app.configs.database import db


@dataclass
class Leads(db.Model):
    
    name: str
    email: str
    phone: str
    creation_date: dt
    last_visit: dt
    visits: int

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False, unique=True)
    creation_date = Column(DateTime, default=dt.now())
    last_visit = Column(DateTime, default=dt.now())
    visits = Column(Integer, default=1)