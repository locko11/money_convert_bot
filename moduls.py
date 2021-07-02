from sqlalchemy.engine import create_engine
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base



engine = create_engine('sqlite:///bot.db')
Base = declarative_base()

class Cache(Base):
    __tablename__ = 'cashe'
    id = Column(Integer, primary_key=True)
    currency = Column(String, unique=True)
    price = Column(Float)
    created = Column(DateTime)

    def __init__(self, currency, price, created):
        self.currency = currency
        self.price = price
        self.created = created

    def __repr__(self):
        return self.currency

Base.metadata.create_all(engine)


