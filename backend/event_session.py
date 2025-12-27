from sqlalchemy.dialects.sqlite import insert
from database.db_init import ENGINE
from sqlalchemy.orm import sessionmaker
from database.models import EventSession, Weather, RaceControl, Lap
from modules.db_tools import get_data_for_event_session, insert_for_weather, get_race_control_messages, get_lap_data
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
            logger.success(f"Event session {i} data prepared and inserted into session.")
            session.commit()
            logger.success(f"Event session {i} successfully committed to database.") 
        except Exception as e:
           logger.error(f"Error loading current_session {i}: {e}. Skipping.")

        try:
            race_control_messages_records = get_race_control_messages(session, session_data)
            stmt_race_control_messages = insert(RaceControl).values(race_control_messages_records)
            session.execute(stmt_race_control_messages)
            logger.success(f"Race control {i} data prepared and inserted into session.")
            session.commit()
            logger.success(f"Race control {i} successfully committed to database.") 
        except Exception as e:
            logger.error(f"Error loading race control messages {i}: {e}. Skipping.")

        laps = session_data.laps

        try:
            weather_records = insert_for_weather(laps, session)
            stmt_weather = insert(Weather).values(weather_records)
            session.execute(stmt_weather)
            logger.success(f"Weather {i} data prepared and inserted into session.")
            session.commit()
            logger.success(f"Weather {i} successfully committed to database.") 
        except Exception as e:
            logger.error(f"Error loading weather {i}: {e}. Skipping.")

        try:
            lap_records = get_lap_data(laps, session)
            stmt_laps = insert(Lap).values(lap_records)
            session.execute(stmt_laps)
            logger.success(f"Lap {i} data prepared and inserted into session.")
            session.commit()
            logger.success(f"Lap {i} successfully committed to database.") 
        except Exception as e:
            session.rollback()
            if 'lap_records' in locals() and len(lap_records) > 0:
                sample = lap_records[0]
                logger.error(f"--- Diagnostic for Lap {i} ---")
                for key, val in sample.items():
                    logger.info(f"Column: {key:20} | Value: {str(val):20} | Type: {type(val)}")
            
            logger.error(f"Failed to load lap {i}. Error: {e}")