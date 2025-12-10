from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.base import Base
from database.models import *

PATH = "backend/database/f1_analysis.db"
ENGINE = create_engine(f"sqlite:///{PATH}", echo=True)

Base.metadata.create_all(ENGINE)
sessionmaker(bind=ENGINE)