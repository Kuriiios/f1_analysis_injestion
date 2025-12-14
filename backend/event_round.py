from sqlalchemy.orm import sessionmaker
from database.db_init import ENGINE
from database.models import *
from modules.db_tools import get_data_for_event_rounds
from loguru import logger
from dotenv import load_dotenv
import os
load_dotenv()

Session = sessionmaker(bind=ENGINE)

logger.remove()
logger.add(sink=os.getenv("LOG_PATH") + "event_round.log", rotation="500 MB", level="INFO")

with Session() as session:
    try:
        event_round_records = get_data_for_event_rounds()
        events = [EventRound(**record) for record in event_round_records]
        session.add_all(events)
        session.commit()

        session.commit()
        logger.success("Event Rounds data committed successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f'Failed to initialize Event Rounds tables. Rolling back. Error: {e}')