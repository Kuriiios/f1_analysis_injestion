import fastf1
import fastf1.plotting
import pandas as pd

session_names = [{"name": "Practice 1"}, {"name": "Practice 2"}, {"name": "Practice 3"}, {"name": "Sprint Qualifying"}, {"name": "Sprint"}, {"name": "Qualifying"}, {"name": "Race"}]
compounds = [{"hardness": "C0"}, {"hardness": "C1"}, {"hardness": "C2"}, {"hardness": "C3"}, {"hardness": "C4"}, {"hardness": "C5"}, {"hardness": "C6"}]
tyres = [{"name": "soft"}, {"name": "medium"}, {"name": "hard"}, {"name": "intermediate"}, {"name": "wet"}, {"name": "unknown"}, ]
drss = [{"status" : "Off"}, {"status" : "Unknown"}, {"status" : "Detected"}, {"status" : "On"}]
wind_directions = [{"cardinal_direction": "N"}, {"cardinal_direction": "NNE"}, {"cardinal_direction": "NE"}, {"cardinal_direction": "ENE"}, {"cardinal_direction": "E"}, {"cardinal_direction": "ESE"}, {"cardinal_direction": "SE"}, {"cardinal_direction": "SSE"}, {"cardinal_direction": "S"}, {"cardinal_direction": "SSW"}, {"cardinal_direction": "SW"}, {"cardinal_direction": "WSW"}, {"cardinal_direction": "W"}, {"cardinal_direction": "WNW"}, {"cardinal_direction": "NW"}, {"cardinal_direction": "NNW"}]

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

drivers_data_manual = [{"name" : "Max Verstappen", "country":"Dutchland"},
        {"name" : "Yuki Tsunoda", "country":"Japan"},
        {"name" : "Arvid Lindblad", "country":"Great Britain"},
        {"name" : "Pierre Gasly", "country":"France"},
        {"name" : "Franco Colapinto", "country":"Argentine"},
        {"name" : "Andrea Kimi Antonelli", "country":"Italia"},
        {"name" : "Kimi Antonelli", "country":"Italia"},
        {"name" : "George Russell", "country":"Great Britain"},
        {"name" : "Fernando Alonso", "country":"Spain"},
        {"name" : "Lance Stroll", "country":"Canada"},
        {"name" : "Charles Leclerc", "country":"Monaco"},
        {"name" : "Arthur Leclerc", "country":"Monaco"},
        {"name" : "Lewis Hamilton", "country":"Great Britain"},
        {"name" : "Alexander Albon", "country":"Thailand"},
        {"name" : "Carlos Sainz", "country":"Spain"},
        {"name" : "Nico Hulkenberg", "country":"Germany"},
        {"name" : "Gabriel Bortoleto", "country":"Brazil"},
        {"name" : "Liam Lawson", "country":"New Zealand"},
        {"name" : "Isack Hadjar", "country":"France"},
        {"name" : "Esteban Ocon", "country":"France"},
        {"name" : "Oliver Bearman", "country":"Great Britain"},
        {"name" : "Ollie Bearman", "country":"Great Britain"},
        {"name" : "Lando Norris", "country":"Great Britain"},
        {"name" : "Oscar Piastri", "country":"Australia"},
        {"name" : "Cian Shields", "country":"Great Britain"},
        {"name" : "Jak Crawford", "country":"America"},
        {"name" : "Patricio O'Ward", "country":"Mexico"},
        {"name" : "Ayumu Iwasa", "country":"Japan"},
        {"name" : "Paul Aron", "country":"Estonia"},
        {"name" : "Luke Browning", "country":"Great Britain"},
        {"name" : "Ryo Hirakawa", "country":"Japan"},
        {"name" : "Frederik Vesti", "country":"Danemark"},
        {"name" : "Antonio Fuoco", "country":"Italia"},
        {"name" : "Alexander Dunne", "country":"Ireland"},
        {"name" : "Felipe Drugovich", "country":"Brazil"},
        {"name" : "Dino Beganovic", "country":"Sweden"},
        {"name" : "Jack Doohan", "country":"Australia"},
        ]
drivers_data_manual = pd.DataFrame(drivers_data_manual)
drivers_all_info = pd.merge(df_final, drivers_data_manual, how='outer', on='name')
drivers_all_info = drivers_all_info.drop_duplicates(['abbreviation'])
drivers_all_info = drivers_all_info.drop_duplicates(['name'], keep='first')
drivers_records = drivers_all_info.to_dict('records')

teams = fastf1.plotting.list_team_names(session)
teams = [{"name":team, "hex_code":fastf1.plotting.get_team_color(team, session)} for team in teams]
df = pd.DataFrame(teams)
teams = [{"name": "Alpine", "abbreviation": "ALP", "country":"France"},
        {"name": "Aston Martin", "abbreviation": "AMR", "country":"Great Britain"},
        {"name": "Ferrari", "abbreviation": "FER", "country":"Italia"},
        {"name": "Haas F1 Team", "abbreviation": "HAA", "country":"America"},
        {"name": "Kick Sauber", "abbreviation": "SAU", "country":"Switz"},
        {"name": "McLaren", "abbreviation": "MCL", "country":"New Zealand"},
        {"name": "Mercedes", "abbreviation": "MER", "country":"German"},
        {"name": "Racing Bulls", "abbreviation": "RBL", "country":"Italia"},
        {"name": "Red Bull Racing", "abbreviation": "RBR", "country":"Great Britain"},
        {"name": "Williams", "abbreviation": "WIL", "country":"Great Britain"},
        ]
df_manual_insert = pd.DataFrame(teams)
df_teams = pd.merge(df, df_manual_insert, how='outer', on='name').drop_duplicates()
teams_records = df_teams.to_dict('records')