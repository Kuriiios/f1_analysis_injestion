from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import sessionmaker
from database.base import Base
from database.models import *
from loguru import logger

PATH = "backend/database/f1_analysis.db"
ENGINE = create_engine(f"sqlite:///{PATH}", echo=True)

Base.metadata.create_all(ENGINE)
Session = sessionmaker(bind=ENGINE)

PATH = 'backend/logs/main.log'
logger.remove()
logger.add(sink=PATH, rotation="500 MB", level="INFO")

with Session() as session:
    try:
        session_names = [{"name": "Practice 1"}, {"name": "Practice 2"}, {"name": "Practice 3"}, {"name": "Sprint Qualifying"}, {"name": "Sprint"}, {"name": "Qualifying"}, {"name": "Race"}]
        stmt_session = insert(SessionName).values(session_names).on_conflict_do_nothing(index_elements=[SessionName.name])
        session.execute(stmt_session)
        logger.success('Session Names ensured in database.')

        compounds = [{"hardness": "C0"}, {"hardness": "C1"}, {"hardness": "C2"}, {"hardness": "C3"}, {"hardness": "C4"}, {"hardness": "C5"}, {"hardness": "C6"}]
        stmt_compound = insert(Compound).values(compounds).on_conflict_do_nothing(index_elements=[Compound.hardness])
        session.execute(stmt_compound)
        logger.success('Compounds ensured in database.')

        tyres = [{"name": "soft"}, {"name": "medium"}, {"name": "hard"}, {"name": "intermediate"}, {"name": "wet"}, {"name": "unknown"}, ]
        stmt_tyre = insert(Tyre).values(tyres).on_conflict_do_nothing(index_elements=[Tyre.name])
        session.execute(stmt_tyre)
        logger.success('Tyres ensured in database.')

        drss = [{"status" : "Off"}, {"status" : "Unknown"}, {"status" : "Detected"}, {"status" : "On"}]
        stmt_drs = insert(Drs).values(drss).on_conflict_do_nothing(index_elements=[Drs.status])
        session.execute(stmt_drs)
        logger.success('DRSs ensured in database.')

        wind_directions = [{"cardinal_direction": "N"}, {"cardinal_direction": "NNE"}, {"cardinal_direction": "NE"}, {"cardinal_direction": "ENE"}, {"cardinal_direction": "E"}, {"cardinal_direction": "ESE"}, {"cardinal_direction": "SE"}, {"cardinal_direction": "SSE"}, {"cardinal_direction": "S"}, {"cardinal_direction": "SSW"}, {"cardinal_direction": "SW"}, {"cardinal_direction": "WSW"}, {"cardinal_direction": "W"}, {"cardinal_direction": "WNW"}, {"cardinal_direction": "NW"}, {"cardinal_direction": "NNW"}]
        stmt_wind = insert(WindDirection).values(wind_directions).on_conflict_do_nothing(index_elements=[WindDirection.cardinal_direction])
        session.execute(stmt_wind)
        logger.success('Wind Directions ensured in database.')

        session.commit()
        logger.success("All initial data committed successfully.")

    except Exception as e:
        session.rollback()
        logger.error(f'Failed to initialize database tables. Rolling back. Error: {e}')