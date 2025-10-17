from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Passenger(Base):
    __tablename__ = "passengers"
    
    passenger_id = Column(Integer, primary_key=True, index=True)
    survived = Column(Boolean, nullable=False)
    pclass = Column(Integer)
    name = Column(String)
    sex = Column(String)
    age = Column(Float)
    sibsp = Column(Integer)
    parch = Column(Integer)
    ticket = Column(String)
    fare = Column(Float)
    cabin = Column(String)
    embarked = Column(String)
