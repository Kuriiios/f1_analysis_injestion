from sqlalchemy.dialects.sqlite import insert
from database.db_init import ENGINE
from sqlalchemy.orm import sessionmaker
from database.models import EventSession, Weather, RaceControl, Lap
from modules.db_tools import get_list_drivers, get_event_session, get_lap_per_driver, get_driver, format_car_data, format_pos_data
import fastf1
import os
import pandas as pd
from dotenv import load_dotenv
from loguru import logger
load_dotenv()

Session = sessionmaker(bind=ENGINE)

logger.remove()
logger.add(sink=os.getenv("LOG_PATH") + "lap.log", rotation="500 MB", level="INFO")

with Session() as session:
    for i in range(1,6):
        try:
            session_data = fastf1.get_session(int(os.getenv("SEASON")), int(os.getenv("ROUND")), i)
            session_data.load()
            laps = session_data.laps

            all_drivers_car_data = []
            all_drivers_pos_data = []

            results_event_session = get_event_session(session, 2025, 5, 'Race')
            results_drivers = get_list_drivers(session, results_event_session)
            list_drivers = list(set([ld.driver.number for ld in results_drivers]))

            for driver_num in list_drivers:

                driver_laps = laps.pick_drivers(driver_num)

                if driver_laps.empty:
                    print(f"Skipping Driver {driver_num}: Not found in FastF1 laps data.")
                    continue

                results = get_lap_per_driver(session, results_event_session, driver_num)
                
                for lap_obj in results:
                    lap_slice = driver_laps.pick_laps(lap_obj.lap_number)

                    if lap_slice.empty:
                        print(
                            f"Skipping Driver {driver_num} Lap {lap_obj.lap_number}: "
                            "Lap not present in FastF1."
                        )
                        continue

                    try:
                        raw_car_slice = lap_slice.get_car_data()
                        raw_pos_slice = lap_slice.get_pos_data()
                    except ValueError as e:
                        print(
                            f"Skipping Driver {driver_num} Lap {lap_obj.lap_number}: {e}"
                        )
                        continue

                    if raw_car_slice.empty or raw_pos_slice.empty:
                        print(
                            f"Skipping Driver {driver_num} Lap {lap_obj.lap_number}: "
                            "No telemetry recorded."
                        )
                        continue

                    car_data = format_car_data(raw_car_slice) 
                    pos_data = format_pos_data(raw_pos_slice)
                    
                    car_data['lap_id'] = lap_obj.id
                    pos_data['lap_id'] = lap_obj.id

                    all_drivers_car_data.append(car_data)
                    all_drivers_pos_data.append(pos_data)

            if all_drivers_car_data:
                final_car_df = pd.concat(all_drivers_car_data, ignore_index=True)
                
            if all_drivers_pos_data:
                final_pos_df = pd.concat(all_drivers_pos_data, ignore_index=True)

        except Exception as e:
           logger.error(f"Error loading lap {i}: {e}. Skipping.")