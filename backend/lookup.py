from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import sessionmaker
from data.third_party_data import SESSION_NAMES, COMPOUNDS, TYRES, DRSS, WIND_DIRECTIONS, DRIVERS_RECORDS, TEAM_RECORDS
from database.db_init import ENGINE, Base
from database.models import *
from loguru import logger
import os
from dotenv import load_dotenv
load_dotenv()

Base.metadata.create_all(ENGINE)
Session = sessionmaker(bind=ENGINE)

logger.remove()
logger.add(sink=os.getenv("LOG_PATH") + "lookup.log", rotation="500 MB", level="INFO")

with Session() as session:
    try:
        stmt_session_name = insert(SessionName).values(SESSION_NAMES).on_conflict_do_nothing(index_elements=[SessionName.name])
        session.execute(stmt_session_name)
        logger.success('Session Names ensured in database.')

        stmt_compound = insert(Compound).values(COMPOUNDS).on_conflict_do_nothing(index_elements=[Compound.hardness])
        session.execute(stmt_compound)
        logger.success('Compounds ensured in database.')

        stmt_tyre = insert(Tyre).values(TYRES).on_conflict_do_nothing(index_elements=[Tyre.name])
        session.execute(stmt_tyre)
        logger.success('Tyres ensured in database.')

        stmt_drs = insert(Drs).values(DRSS).on_conflict_do_nothing(index_elements=[Drs.status])
        session.execute(stmt_drs)
        logger.success('DRSs ensured in database.')

        stmt_wind = insert(WindDirection).values(WIND_DIRECTIONS).on_conflict_do_nothing(index_elements=[WindDirection.cardinal_direction])
        session.execute(stmt_wind)
        logger.success('Wind Directions ensured in database.')

        stmt_drivers = insert(Driver).values(DRIVERS_RECORDS).on_conflict_do_nothing(index_elements=[Driver.name])
        session.execute(stmt_drivers)
        logger.success('Drivers ensured in database.')

        stmt_teams = insert(Team).values(TEAM_RECORDS).on_conflict_do_nothing(index_elements=[Team.name])
        session.execute(stmt_teams)
        logger.success('Teams ensured in database.')
        
        session.commit()
        logger.success('All initial data committed successfully.')

    except Exception as e:
        session.rollback()
        logger.error(f'Failed to initialize database tables. Rolling back. Error: {e}')