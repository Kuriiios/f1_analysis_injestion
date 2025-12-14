from database.db_init import ENGINE
from sqlalchemy.orm import sessionmaker
from database.models import EventSession
from modules.db_tools import get_data_for_event_session
import fastf1
import os
from dotenv import load_dotenv
from loguru import logger
load_dotenv()

Session = sessionmaker(bind=ENGINE)

logger.remove()
logger.add(sink=os.getenv("LOG_PATH") + "event_session.log", rotation="500 MB", level="INFO")

with Session() as session:
    for i in range(1,6):
        try:
            session_data = fastf1.get_session(int(os.getenv("SEASON")), int(os.getenv("ROUND")), i)
            session_data.load()
            
            session_date_param, event_round, session_name = get_data_for_event_session(session, i)
            event_session = EventSession(date=session_date_param, session_name=session_name, event_round=event_round)
            session.add(event_session)
            session.commit()
            logger.success('Event Session ensured in database.')

        except Exception as e:
            print(f"Error loading current_session {i}: {e}. Skipping.")
