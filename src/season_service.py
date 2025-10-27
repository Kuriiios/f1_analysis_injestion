from fastapi import FastAPI
import fastf1
import pandas as pd
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def get_event_round(year):
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    event_round = schedule[["RoundNumber", "Country", "Location", "EventName", "EventDate", "EventFormat"]].copy()
    event_round.loc[event_round["EventFormat"] == "sprint_qualifying", "IsSprintEvent"] = 1
    event_round["IsSprintEvent"] = event_round["IsSprintEvent"].fillna(0).astype(bool)
    event_round["Year"] = year
    event_round = event_round.drop(labels='EventFormat', axis=1)
    event_round = event_round.rename(columns={
                                "RoundNumber" : "roundNumber",
                                "Country": "country",
                                "Location": "location",
                                "EventName": "eventName",
                                "EventDate": "eventDate",
                                "IsSprintEvent": "isSprintEvent",
                                "Year": "year"})
        
    tyres = {}
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'tyre_compound/1.0 (cyril.leconte07@gmail.com)'
    })

    with ThreadPoolExecutor(max_workers=24) as executor:
        future_to_event = {executor.submit(get_tyre_info_api, year, event, session): event for event in schedule.EventName}
        
        for future in as_completed(future_to_event):
            event_name, c_levels = future.result()
            tyres[event_name] = c_levels

    tyres_df = pd.DataFrame.from_dict(columns=['hard', 'medium', 'soft'], data = tyres, orient="index")

    event_round = event_round.merge(tyres_df, left_on="eventName", right_index=True, how="left")
    event_round = event_round.iloc[:, [6, 0, 1 , 2, 3, 4, 5, 9, 8 , 7]]
    return event_round

session_mapper= {
    "Practice 1": 1,
    "Practice 2": 2,
    "Practice 3": 3,
    "Sprint Qualifying": 4,
    "Sprint": 5,
    "Qualifying": 6,
    "Race": 7,
}

app=FastAPI()
@app.get("/event-rounds/{year}")
def get_races(year: int):
    event_round = get_event_round(year)
    return event_round.to_dict(orient="records")

@app.get("/sessions/{year}")
def get_all_sessions(year: int):
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        all_sessions = []
        for round_number in range(1, len(schedule)+1):
            try:
                event = fastf1.get_event(year, round_number)
                for i in range(1,6):
                    sess = event.get_session(i)
                    all_sessions.append({
                                "roundNumber": round_number,
                                "sessionNameId": session_mapper[sess.name],
                                "sessionDate": pd.to_datetime(sess.date).strftime("%Y-%m-%dT%H:%M:%S"),
                            })
            except Exception as e:
                return {"error": str(e)}
        return all_sessions
    except Exception as e:
                return {"error": str(e)}

@app.get("/session/{year}/{round_number}")
def get_sessions(year: int, round_number: int):
    try:
        event = fastf1.get_event(year, round_number)
        sessions = []
        for i in range(1,6):
            sess = event.get_session(i)
            sessions.append({
                        "roundNumber": round_number,
                        "sessionNameId": session_mapper[sess.name],
                        "sessionDate": pd.to_datetime(sess.date).strftime("%Y-%m-%dT%H:%M:%S"),
                    })
        return sessions
    except Exception as e:
        return {"error": str(e)}