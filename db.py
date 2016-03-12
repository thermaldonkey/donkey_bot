from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import DB_URL

engine = create_engine(DB_URL, echo=True)
Base = declarative_base()

def connect():
    Session = sessionmaker(bind=engine)
    return Session()

