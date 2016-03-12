from sqlalchemy import Column, Integer, String
from db import Base

class Viewer(Base):
    __tablename__ = 'viewers'

    id = Column(Integer, primary_key=True, nullable=False)
    nickname = Column(String, nullable=False)
    points = Column(Integer, nullable=False, server_default='0', default=0)

    def __repr__(self):
        return "<User(nickname='{}', points='{}')>".format(self.nickname, self.points)

