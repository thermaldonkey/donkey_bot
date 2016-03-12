'''Drops all tables and rebuilds based on the schema as defined by the models.py file.'''
from db import engine
# We need this from the models file because for whatever awesome reason the metadata object is only
# bound to the tables we need it to drop and create AFTER those tables have been declared as
# models.
from models import Base

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

