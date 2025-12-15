from sqlalchemy import select
from database.models import EventRound, SessionName, EventSession
import fastf1
import fastf1.plotting
import os
from dotenv import load_dotenv
import pandas as pd
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import sessionmaker
from database.models import Compound
from database.db_init import ENGINE
from loguru import logger
load_dotenv()

def get_data_driver_and_team_records(drivers_data_input, teams_data_input):
        df_final = pd.DataFrame()
        for round in range(1,25):
            for event_session in [1,4,5]:
                session = fastf1.get_session(2025, round, event_session)
                session.load(telemetry=False, weather=False, messages=False)

                drivers = fastf1.plotting.list_driver_names(session=session)
                drivers_abbreviation =[fastf1.plotting.get_driver_abbreviation(driver, session) for driver in drivers]
                df = pd.DataFrame([session.get_driver(abbreviation) for abbreviation in drivers_abbreviation])
                df = df[['DriverNumber', 'Abbreviation', 'FullName', 'TeamColor']].rename(columns={'DriverNumber':'number', 'Abbreviation':'abbreviation', 'FullName':'name', 'TeamColor':'hex_code'})
                df_final = pd.concat([df, df_final]).drop_duplicates()
        drivers_data_manual = drivers_data_input
        drivers_data_manual = pd.DataFrame(drivers_data_manual)
        drivers_all_info = pd.merge(df_final, drivers_data_manual, how='outer', on='name')
        drivers_all_info = drivers_all_info.drop_duplicates(['abbreviation'])
        drivers_all_info = drivers_all_info.drop_duplicates(['name'], keep='first')
        drivers_records = drivers_all_info.to_dict('records')

        teams = fastf1.plotting.list_team_names(session)
        teams = [{"name":team, "hex_code":fastf1.plotting.get_team_color(team, session)} for team in teams]
        df = pd.DataFrame(teams)
        teams = teams_data_input
        df_manual_insert = pd.DataFrame(teams)
        df_teams = pd.merge(df, df_manual_insert, how='outer', on='name').drop_duplicates()
        teams_records = df_teams.to_dict('records')

        return drivers_records, teams_records

def insert_for_weather(laps, session):
    weather_df = laps.get_weather_data().dropna().drop_duplicates()
    weather_df = weather_df.rename(columns={'Time':'time', 'AirTemp': 'air_temp', 'Humidity': 'humidity', 'Pressure': 'pressure', 'Rainfall':'is_rainfall', 'TrackTemp':'track_temp',
        'WindDirection':'wind_direction', 'WindSpeed':'wind_speed'})
    event_session_id = get_data_for_weather(session, int(os.getenv("SEASON")), int(os.getenv("ROUND")), laps.session.name)
    weather_df['event_session_id'] = event_session_id
    print(event_session_id)
    if event_session_id is None:
        logger.error("EventSession ID not found for bulk insert.")
        return []
    weather_records = weather_df.to_dict('records')
    return weather_records

def get_data_for_weather(session, year, round_number, session_name):   
    event_session = (
        session.query(EventSession)
        .join(EventSession.event_round)
        .join(EventSession.session_name)
        .filter(EventRound.year == year)
        .filter(EventRound.round_number == round_number)
        .filter(SessionName.name == session_name)
        .one_or_none()
    )
    return event_session.id

def get_data_for_event_session(session, i):
    event = fastf1.get_event(int(os.getenv("SEASON")), int(os.getenv("ROUND")))

    event_round = session.execute(
        select(EventRound).where(EventRound.year == int(os.getenv("SEASON")), EventRound.round_number == int(os.getenv("ROUND")) )
    ).scalar_one_or_none()

    match i:
        case 1:
            session_date_param = event.Session1Date.date()
            session_name_param = event.Session1
        case 2:
            session_date_param = event.Session2Date.date()
            session_name_param = event.Session2
        case 3:
            session_date_param = event.Session3Date.date()
            session_name_param = event.Session3
        case 4:
            session_date_param = event.Session4Date.date()
            session_name_param = event.Session4
        case 5:
            session_date_param = event.Session5Date.date()
            session_name_param = event.Session5

    session_name = session.execute(
        select(SessionName).where(SessionName.name == session_name_param)
    ).scalar_one_or_none()

    return session_date_param, event_round, session_name

def get_data_for_event_rounds():
    schedule = fastf1.get_event_schedule(int(os.getenv('SEASON')), include_testing=False)
    event_round = schedule[["RoundNumber", "Country", "Location", "EventName", "EventDate", "EventFormat"]].copy()
    event_round.loc[event_round["EventFormat"] == "sprint_qualifying", "IsSprintEvent"] = 1
    event_round["IsSprintEvent"] = event_round["IsSprintEvent"].fillna(0).astype(bool)
    event_round["Year"] = int(os.getenv('SEASON'))
    event_round = event_round.drop(labels='EventFormat', axis=1)
    event_round = event_round.rename(columns={
                                "RoundNumber" : "round_number",
                                "Country": "country",
                                "Location": "location",
                                "EventName": "name",
                                "EventDate": "date",
                                "IsSprintEvent": "is_sprint_event",
                                "Year": "year"})

    tyres_df = fetch_tyres(os.getenv('SEASON'), schedule)

    event_round = event_round.merge(tyres_df, left_on="name", right_index=True, how="left")
    event_round = event_round[['name', 'round_number', 'year', 'date', 'country', 'location', 'is_sprint_event', 'soft_compound', 'medium_compound', 'hard_compound']]

    event_round_records = event_round.to_dict('records')
    return event_round_records

def fetch_tyres(year, schedule):
    Session = sessionmaker(bind=ENGINE)

    compound_cache = {}

    def get_compound(hardness):
        if not hardness or hardness == '0':
            return None
        hardness = f"C{hardness}" if not hardness.startswith("C") else hardness
        if hardness not in compound_cache:
            with Session() as session:
                compound_cache[hardness] = session.execute(
                    select(Compound).where(Compound.hardness == hardness)
                ).scalar_one_or_none()
        return compound_cache[hardness]

    def parse_tyres(content: str):
        pattern = re.compile(r'C([1-6])')
        matches = pattern.findall(content)
        if len(matches) >= 3:
            return sorted(list(set(matches)))[:3]
        # fallback to whole content
        matches_fallback = pattern.findall(content)
        return sorted(list(set(matches_fallback)))[:3] if matches_fallback else ['0', '0', '0']

    def fetch_event(event_name, session):
        url_name = re.sub(r'\s+', '_', event_name.strip())
        api_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles={year}_{url_name}&rvprop=content&format=json&formatversion=2"
        try:
            resp = session.get(api_url, timeout=10)
            resp.raise_for_status()
            pages = resp.json().get('query', {}).get('pages', [])
            if pages and 'missing' not in pages[0]:
                content = pages[0]['revisions'][0]['content']
                section_match = re.search(r'==\s*Tyre choices\s*==(.*?)(?:==|$)', content, re.DOTALL)
                return event_name, parse_tyres(section_match.group(1) if section_match else content)
        except Exception as e:
            print(f"Error fetching {event_name}: {e}")
        return event_name, ['0', '0', '0']

    tyres_dict = {}
    with requests.Session() as http_session:
        http_session.headers.update({'User-Agent': f'tyre_compound/1.0 ({os.getenv("email")})'})
        with ThreadPoolExecutor(max_workers=24) as executor:
            futures = {executor.submit(fetch_event, event, http_session): event for event in schedule.EventName}
            for future in as_completed(futures):
                event_name, compounds = future.result()
                tyres_dict[event_name] = compounds

    df = pd.DataFrame.from_dict(
        tyres_dict,
        orient="index",
        columns=["hard_compound", "medium_compound", "soft_compound"]
    )

    return df.applymap(get_compound)
