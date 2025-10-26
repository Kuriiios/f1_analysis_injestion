import fastf1
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, insert, and_, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy as sa

# Enable caching (important for speed)
#fastf1.Cache.enable_cache("./cache")

DATABASE_URL = "postgresql+psycopg2://creator:roadtose@localhost:5432/f1_data"

SEASON = 2025
ROUND = 1

session_mapper= {
    "Practice 1": 1,
    "Practice 2": 2,
    "Practice 3": 3,
    "Sprint Qualifying": 4,
    "Sprint": 5,
    "Qualifying": 6,
    "Race": 7,
}

compound_mapper = {
    "SOFT": 1,
    "MEDIUM" : 2,
    "HARD": 3,
    "INTERMEDIATE" : 4,
    "WET" : 5,
    "UNKNOWN" : 6,
}

drs_mapper = {
    "Off": 0,
    "Off" : 1,
    "Unknown": 2,
    "Unknown": 3,
    "Detected" : 8,
    "On" : 10,
    "On" : 12,
    "On" : 14,
}

engine = sa.create_engine(DATABASE_URL, echo=True)
metadata = sa.MetaData()
metadata.reflect(bind=engine)


CarData = metadata.tables['car_data']
Driver = metadata.tables['driver']
Dta = metadata.tables['dta']
Lap = metadata.tables['lap']
PosData = metadata.tables['pos_data']
Session = metadata.tables['event_session']
SessionName = metadata.tables['session_name']
Team = metadata.tables['team']
Weather = metadata.tables['weather']

SessionLocal = sessionmaker(bind=engine)

with SessionLocal() as db:

    driver_map = {row.driver_number: row.driver_id for row in db.query(Driver).all()}
    team_map = {row.team_name: row.team_id for row in db.query(Team).all()}

    for i in range(1, 6): 
        try:
            session_data = fastf1.get_session(SEASON, ROUND, i)
            session_data.load()
        except Exception as e:
            print(f"Error loading current_session {i}: {e}. Skipping.")
            continue

        laps = session_data.laps
        session_row = db.execute(
            sa.select(Session).where(Session.c.session_name_id == session_mapper[session_data.name])
        ).fetchone()
        if not session_row:
            print(f"Session {session_data.name} not found in DB. Skipping.")
            continue

        try:
            weather_df = laps.get_weather_data().replace({pd.NaT: None, np.nan: None}).copy()
            if not weather_df.empty:
                weather_df['event_session_id'] = session_row.event_session_id
                weather_df['time_'] = pd.to_timedelta(weather_df['Time']).dt.total_seconds()
                weather_df = weather_df.drop_duplicates(
                    subset=["event_session_id", "time_", "WindDirection", "AirTemp", "Humidity",
                            "Pressure", "Rainfall", "TrackTemp", "WindSpeed"]
                )
                
                weather_dicts = weather_df.rename(columns={
                    'time_': 'time', 'AirTemp': 'air_temp', 'Humidity': 'humidity', 
                    'Pressure': 'pressure', 'Rainfall': 'is_rainfall','TrackTemp': 'track_temp', 
                    'WindDirection': 'wind_direction','WindSpeed': 'wind_speed',
                }).to_dict(orient="records")

                if weather_dicts:
                    db.execute(insert(Weather), weather_dicts)
                    db.commit()
        
        except Exception as e:
            db.rollback()
            import traceback
            traceback.print_exc()
            print(f"Error loading weather: {e}. Skipping.")
        
        for driver_number in session_data.drivers:
            driver_id = driver_map.get(int(driver_number))
            if not driver_id:
                print(f"Driver {driver_number} not found. Skipping.") 
                continue

            driver_team_name = session_data.get_driver(str(driver_number))['TeamName']
            team_id = team_map.get(driver_team_name)
            if not team_id:
                print(f"Team {driver_team_name} not found. Skipping.")
                continue

            dta_row = db.execute(
                sa.select(Dta.c.dta_id).where(
                    and_(
                        Dta.c.driver_id == driver_id,
                        Dta.c.team_id == team_id,
                        Dta.c.event_session_id == session_row.event_session_id
                    )
                )
            ).fetchone()

            if dta_row:
                dta_id = dta_row[0]
            else:
                dta_id = db.execute(
                    insert(Dta).values(
                        driver_id=driver_id,
                        team_id=team_id,
                        event_session_id=session_row.event_session_id
                    ).returning(Dta.c.dta_id)
                ).scalar_one()

            try:
                driver_laps = laps.pick_drivers(driver_number)
                if not driver_laps.empty:
                    driver_laps = driver_laps.replace({pd.NaT: None, np.nan: None}).copy()
                    driver_laps = driver_laps[
                        driver_laps['LapStartDate'].notna()                    
                    ]

                    timedelta_cols = [
                        'LapTime','PitOutTime','PitInTime','Sector1Time','Sector2Time','Sector3Time',
                        'Sector1SessionTime','Sector2SessionTime','Sector3SessionTime','LapStartTime'
                    ]

                    for col in timedelta_cols:
                        driver_laps[col + '_ms'] = driver_laps[col].apply(
                            lambda x: int(x.total_seconds()*1000) if pd.notna(x) else None
                        )

                    driver_laps['dta_id'] = dta_id
                    driver_laps['LapStartDate'] = pd.to_datetime(driver_laps['LapStartDate'])
                    driver_laps['Compound'] = driver_laps['Compound'].apply(
                        lambda x : compound_mapper[x]
                        )
                    
                    int_cols = [
                        'LapTime_ms',
                        'PitOutTime_ms',
                        'PitInTime_ms',
                        'Sector1Time_ms',
                        'Sector2Time_ms',
                        'Sector3Time_ms',
                        'Sector1SessionTime_ms',
                        'Sector2SessionTime_ms',
                        'Sector3SessionTime_ms',
                        'LapStartTime_ms',
                        'LapNumber',
                        'Position',
                        'Stint',
                        'TyreLife'
                    ]
                    driver_laps = driver_laps.replace({pd.NaT: None, np.nan: None}).copy()
                    for col in int_cols:
                        driver_laps[col] = driver_laps[col].apply(
                            lambda x: int(x) if x is not None else 0
                        )

                    lap_dicts = driver_laps[[
                        'dta_id','Compound','LapTime_ms','LapNumber','Stint',
                        'PitOutTime_ms','PitInTime_ms','Sector1Time_ms','Sector2Time_ms','Sector3Time_ms',
                        'Sector1SessionTime_ms','Sector2SessionTime_ms','Sector3SessionTime_ms',
                        'SpeedI1','SpeedI2','SpeedFL','SpeedST',
                        'IsPersonalBest','TyreLife','LapStartTime_ms','LapStartDate',
                        'Position','TrackStatus','Deleted', 'IsAccurate'
                    ]].rename(columns={
                        'Compound': 'compound_id','LapTime_ms':'laptime_ms','LapNumber':'lap_number','Stint':'stint',
                        'PitOutTime_ms':'pit_out_time','PitInTime_ms':'pit_in_time',
                        'Sector1Time_ms':'sector1_time','Sector2Time_ms':'sector2_time','Sector3Time_ms':'sector3_time',
                        'Sector1SessionTime_ms':'sector1_session_time','Sector2SessionTime_ms':'sector2_session_time',
                        'Sector3SessionTime_ms':'sector3_session_time',
                        'SpeedI1':'speed_i1','SpeedI2':'speed_i2','SpeedFL':'speed_fl','SpeedST':'speed_st',
                        'IsPersonalBest':'is_personal_best','TyreLife':'tyre_life','LapStartTime_ms':'lap_start_time',
                        'LapStartDate':'lap_start_date','Position':'position','TrackStatus':'track_status','Deleted':'is_deleted', 'IsAccurate':'is_accurate'
                    }).to_dict(orient='records')
                    
                    if lap_dicts:
                        db.execute(insert(Lap), lap_dicts)
                        db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error Lap: {e}. Skipping.")

            try:
                driver_car_data = laps.pick_drivers(driver_number).get_car_data().add_track_status().add_distance().add_differential_distance().add_driver_ahead().add_relative_distance()
                driver_car_data = driver_car_data.replace({pd.NaT: None, np.nan: None}).copy()
                driver_car_data = driver_car_data.fillna({'RelativeDistance': 0, 'DistanceToDriverAhead': 0})
                driver_car_data = driver_car_data.drop(columns='DriverAhead').copy()
                if not driver_car_data.empty:
                    driver_car_data['dta_id'] = dta_id
                    driver_car_data['time_'] = driver_car_data['Time'].dt.total_seconds()
                    driver_car_data['SessionTime'] = driver_car_data['SessionTime'].dt.total_seconds()
                    driver_car_data['Date'] = pd.to_datetime(driver_car_data['Date'])
                    driver_car_data['DRS'] = driver_car_data['DRS'].map(drs_mapper).fillna(0)

                    car_dicts = driver_car_data[[
                        'dta_id', 'Date', 'time_', 'SessionTime', 'RPM', 'Speed', 'nGear', 'Throttle',
                        'Brake', 'DRS', 'TrackStatus', 'Distance', 'DifferentialDistance',
                        'RelativeDistance', 'DistanceToDriverAhead'
                    ]].rename(columns={
                        'Date':'date_time', 'time_':'time', 'SessionTime':'session_time','RPM':'rpm','Speed':'speed',
                        'nGear':'n_gear','Throttle':'throttle','Brake':'is_braking','DRS':'drs_id',
                        'TrackStatus':'track_status_id','Distance':'distance',
                        'DifferentialDistance':'differential_distance',
                        'RelativeDistance':'relative_distance',
                        'DistanceToDriverAhead':'distance_driver_ahead'
                    }).to_dict(orient='records')

                    if car_dicts:
                        db.execute(insert(CarData), car_dicts)
                        db.commit()
            except Exception as e:
                db.rollback()
                import traceback
                traceback.print_exc()
                print(f"Error CarData: {e}. Skipping.")

            try:
                driver_pos_data = laps.pick_drivers(driver_number).get_pos_data().add_track_status()
                driver_pos_data = driver_pos_data.replace({pd.NaT: None, np.nan: None}).copy()
                if not driver_pos_data.empty:
                    driver_pos_data['dta_id'] = dta_id
                    driver_pos_data['time_'] = driver_pos_data['Time'].dt.total_seconds()
                    driver_pos_data['SessionTime'] = driver_pos_data['SessionTime'].dt.total_seconds()
                    driver_pos_data['Date'] = pd.to_datetime(driver_pos_data['Date'])
                    driver_pos_data['Status'] = driver_pos_data['Status'].eq("OnTrack")

                    pos_dicts = driver_pos_data[[
                        'dta_id', 'Date', 'time_', 'SessionTime', 'X', 'Y', 'Z', 'Status', 'TrackStatus'
                    ]].rename(columns={
                        'Date':'date_time', 'time_':'time', 'SessionTime':'session_time','X':'x','Y':'y','Z':'z',
                        'Status':'is_car_on_track','TrackStatus':'track_status_id'
                    }).to_dict(orient='records')

                    if pos_dicts:
                        db.execute(insert(PosData), pos_dicts)
                        db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error PosData: {e}. Skipping.")

        db.commit()
