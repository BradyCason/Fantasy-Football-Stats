import requests
import re
import pandas as pd

def get_event_ids(year, week):
    url = f"https://nfl-football-api.p.rapidapi.com/nfl-events?year={str(year)}"

    headers = {
        "x-rapidapi-host": "nfl-football-api.p.rapidapi.com",
        "x-rapidapi-key": "826c8c237cmsh093c58ff216e09bp1d9846jsn7846b2e6854d"  # Replace with your API key
    }

    # Send the GET request
    response = requests.get(url, headers=headers)

    event_ids = []

    if response.status_code == 200:
        data = response.json()
        for event in data["events"]:
            if event["week"]["number"] == int(week):
                event_ids.append(event["id"])
    else:
        print(f"Error: {response.status_code}, {response.text}")

    print(f"Found {str(len(event_ids))} games in {str(year)} week {str(week)}")
    return event_ids

def add_player(name):
    global db
    if (name not in db.keys()):
        db[name] = {"kicking_yards": 0, "kicks_made": 0, "passing_yards": 0, "rushing_yards": 0, "receiving_yards": 0, "touchdowns": 0}

def get_game_data(game_id):
    global db

    url = "https://nfl-football-api.p.rapidapi.com/nfl-scoringplays"
    querystring = {"id": game_id}  # Replace with the desired game ID

    headers = {
        "x-rapidapi-host": "nfl-football-api.p.rapidapi.com",
        "x-rapidapi-key": "826c8c237cmsh093c58ff216e09bp1d9846jsn7846b2e6854d"  # Replace with your API key
    }

    # Send the GET request
    response = requests.get(url, headers=headers, params=querystring)

    # Check the status and print the response
    if response.status_code == 200:
        data = response.json()
        if (len(data) == 0):
            print(f"No data for Game ID: {game_id}")
            return
        for play in data["scoringPlays"]:
            if (play["type"]["text"]) == "Field Goal Good":
                pattern = r"(?P<kicker>[\w\s\.]+?)\s(?P<yards>\d+)\sYd"
                match = re.search(pattern, play["text"])
                if match:
                    kicker = match.group("kicker")
                    yards = match.group(2)
                else:
                    print(play["type"]["text"])
                    print("No match found for string: " + play["text"])
                add_player(kicker)
                db[kicker]["kicking_yards"] += int(yards)
                db[kicker]["kicks_made"] += 1
            elif (play["type"]["text"]) == "Passing Touchdown":
                pattern = r"(?P<receiver>[\w\s\.]+?)\s(?P<yards>\d+)\sYd.*?from\s(?P<passer>[\w\s\.]+?)(?:\s\(|$)"
                match = re.search(pattern, play["text"])
                if match:
                    receiver = match.group("receiver")
                    yards = match.group(2)
                    passer = match.group("passer")
                else:
                    print(play["type"]["text"])
                    print("No match found for string: " + play["text"])
                add_player(receiver)
                add_player(passer)
                db[receiver]["receiving_yards"] += int(yards)
                db[receiver]["touchdowns"] += 1
                db[passer]["passing_yards"] += int(yards)
                db[passer]["touchdowns"] += 1
            elif (play["type"]["text"]) == "Rushing Touchdown":
                pattern = r"(?P<rusher>[\w\s\.]+?)\s(?P<yards>\d+)\sYd"
                match = re.search(pattern, play["text"])
                if match:
                    rusher = match.group("rusher")
                    yards = match.group(2)
                else:
                    print("No match found for string: " + play["text"])
                add_player(rusher)
                db[rusher]["rushing_yards"] += int(yards)
                db[rusher]["touchdowns"] += 1
            else:
                pattern = r"(?P<rusher>[\w\s\.]+?)\s(?P<yards>\d+)\sYd"
                match = re.search(pattern, play["text"])
                if match:
                    rusher = match.group("rusher")
                    yards = match.group(2)
                else:
                    print("No match found for string: " + play["text"])
                add_player(rusher)
                db[rusher]["rushing_yards"] += int(yards)
                db[rusher]["touchdowns"] += 1
                
    else:
        print(f"Error: {response.status_code}, {response.text}")

def create_file(year, week):
    global db
    df = pd.DataFrame.from_dict(db, orient="index")

    df.to_excel(f"week{str(week)}-{str(year)}-nfl-player-stats.xlsx")

def main():
    global db
    db = {}

    year = int(input("Year: ").strip())
    week = int(input("Week").strip())

    event_ids = get_event_ids(year, week)
    for id in event_ids:
        get_game_data(id)

    create_file(year, week)

if __name__ == "__main__":
    main()