from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import database_configuration


engine = create_engine(database_configuration.get('url'))
session = sessionmaker(engine)
base = declarative_base()
