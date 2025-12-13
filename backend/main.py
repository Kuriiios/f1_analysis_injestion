from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import sessionmaker
from database.data.third_party_data import session_names, compounds, tyres, drss, wind_directions, drivers_records, teams_records
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
        stmt_session = insert(SessionName).values(session_names).on_conflict_do_nothing(index_elements=[SessionName.name])
        session.execute(stmt_session)
        logger.success('Session Names ensured in database.')

        stmt_compound = insert(Compound).values(compounds).on_conflict_do_nothing(index_elements=[Compound.hardness])
        session.execute(stmt_compound)
        logger.success('Compounds ensured in database.')

        stmt_tyre = insert(Tyre).values(tyres).on_conflict_do_nothing(index_elements=[Tyre.name])
        session.execute(stmt_tyre)
        logger.success('Tyres ensured in database.')

        stmt_drs = insert(Drs).values(drss).on_conflict_do_nothing(index_elements=[Drs.status])
        session.execute(stmt_drs)
        logger.success('DRSs ensured in database.')

        stmt_wind = insert(WindDirection).values(wind_directions).on_conflict_do_nothing(index_elements=[WindDirection.cardinal_direction])
        session.execute(stmt_wind)
        logger.success('Wind Directions ensured in database.')

        stmt_drivers = insert(Driver).values(drivers_records).on_conflict_do_nothing(index_elements=[Driver.name])
        session.execute(stmt_drivers)
        logger.success('Drivers ensured in database.')

        stmt_teams = insert(Team).values(teams_records).on_conflict_do_nothing(index_elements=[Team.name])
        session.execute(stmt_teams)
        logger.success('Teams ensured in database.')

        session.commit()
        logger.success("All initial data committed successfully.")

    except Exception as e:
        session.rollback()
        logger.error(f'Failed to initialize database tables. Rolling back. Error: {e}')