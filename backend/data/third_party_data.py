# External data (session_names, compounds, tyres, drss, wind_directions, drivers_records, teams_records)
from modules.db_tools import get_data_driver_and_team_records


drivers_data_input = [{"name" : "Max Verstappen", "country":"Dutchland"},
        {"name" : "Yuki Tsunoda", "country":"Japan"},
        {"name" : "Arvid Lindblad", "country":"Great Britain"},
        {"name" : "Pierre Gasly", "country":"France"},
        {"name" : "Franco Colapinto", "country":"Argentine"},
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

teams_data_input = [{"name": "Alpine", "abbreviation": "ALP", "country":"France"},
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

SESSION_NAMES = [{"name": "Practice 1"}, {"name": "Practice 2"}, {"name": "Practice 3"}, {"name": "Sprint Qualifying"}, {"name": "Sprint"}, {"name": "Qualifying"}, {"name": "Race"}]
COMPOUNDS = [{"hardness": "C0"}, {"hardness": "C1"}, {"hardness": "C2"}, {"hardness": "C3"}, {"hardness": "C4"}, {"hardness": "C5"}, {"hardness": "C6"}]
TYRES = [{"name": "soft"}, {"name": "medium"}, {"name": "hard"}, {"name": "intermediate"}, {"name": "wet"}, {"name": "unknown"}, ]
DRSS = [{"status" : "Off"}, {"status" : "Unknown"}, {"status" : "Detected"}, {"status" : "On"}]
WIND_DIRECTIONS = [{"cardinal_direction": "N"}, {"cardinal_direction": "NNE"}, {"cardinal_direction": "NE"}, {"cardinal_direction": "ENE"}, {"cardinal_direction": "E"}, {"cardinal_direction": "ESE"}, {"cardinal_direction": "SE"}, {"cardinal_direction": "SSE"}, {"cardinal_direction": "S"}, {"cardinal_direction": "SSW"}, {"cardinal_direction": "SW"}, {"cardinal_direction": "WSW"}, {"cardinal_direction": "W"}, {"cardinal_direction": "WNW"}, {"cardinal_direction": "NW"}, {"cardinal_direction": "NNW"}]
DRIVERS_RECORDS, TEAM_RECORDS = get_data_driver_and_team_records(drivers_data_input, teams_data_input)
