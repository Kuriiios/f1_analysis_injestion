from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
load_dotenv()

Base = declarative_base()

ENGINE = create_engine(f"sqlite:///{os.getenv('DATABASE_PATH')}", echo=True)