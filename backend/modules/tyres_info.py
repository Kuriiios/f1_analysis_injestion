import requests
import re
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from sqlalchemy import select
from database.models import Compound
from sqlalchemy.orm import sessionmaker
from database.db_init import ENGINE
load_dotenv()

Session = sessionmaker(bind=ENGINE)

def get_compound(hardness: str) -> Compound:
    with Session() as session:
        compound = session.execute(
            select(Compound).where(Compound.hardness == hardness)
        ).scalar_one_or_none()

        return compound

compound_cache = {}

def get_cached_compound(hardness):
    if hardness == '0' or hardness is None:
        return None

    hardness = f"C{hardness}" if not hardness.startswith("C") else hardness

    if hardness not in compound_cache:
        compound_cache[hardness] = get_compound(hardness)

    return compound_cache[hardness]


def get_tyre_info_api(year , event_name, session):
    event_url_name = re.sub(r'\s+', '_', event_name.strip())
    
    api_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles={year}_{event_url_name}&rvprop=content&format=json&formatversion=2"

    try:
        response = session.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'pages' in data['query'] and 'missing' not in data['query']['pages'][0]:
            page_content = data['query']['pages'][0]['revisions'][0]['content']
             
            tyre_section_match = re.search(r'==\s*Tyre choices\s*==(.*?)==', page_content, re.DOTALL)
            if tyre_section_match:
                tyre_section_content = tyre_section_match.group(1)
                found_compound_levels = set()
                pattern = re.compile(r'C[1-6]')
                matches_with_C = pattern.findall(tyre_section_content)
                matches = list(map(lambda i: i[1:], matches_with_C))

                if matches:
                    found_compound_levels.update(matches)

                compound_levels_list = sorted(list(found_compound_levels))
                if len(compound_levels_list) == 3:
                    return event_name, compound_levels_list
                else:
                    found_compound_levels_fallback = set()
                    matches_fallback = pattern.findall(page_content)
                    if matches_fallback:
                        found_compound_levels_fallback.update(matches_fallback)
                    
                    compound_levels_list_fallback = sorted(list(found_compound_levels_fallback), key=lambda x: int(x[1:]))

                    if len(compound_levels_list_fallback) >= 3:
                        return event_name, compound_levels_list_fallback[:3]
                    else:
                        return event_name, ['0', '0', '0']
            else:
                return event_name, ['0', '0', '0']
        else:
            return event_name, ['0', '0', '0']
             
    except (requests.exceptions.RequestException, Exception) as err:
        print(f"Error for {event_name}: {err}. Setting default values.")
        return event_name, ['0', '0', '0']


def get_tyres_info(year, schedule):
    tyres = {}
    http_session = requests.Session()
    http_session.headers.update({
        'User-Agent': f'tyre_compound/1.0 ({os.getenv('email')})'
    })

    with ThreadPoolExecutor(max_workers=24) as executor:
        future_to_event = {executor.submit(get_tyre_info_api, year, event, http_session): event for event in schedule.EventName}
        
        for future in as_completed(future_to_event):
            event_name, c_levels = future.result()
            tyres[event_name] = c_levels

    tyres_df = pd.DataFrame.from_dict(
        tyres,
        orient="index",
        columns=["hard_compound", "medium_compound", "soft_compound"]
)    
    for col in tyres_df.columns:
        tyres_df[col] = tyres_df[col].apply(
        lambda h: get_cached_compound(h)
        )
    return tyres_df
