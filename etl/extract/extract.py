"""This script will extract live data from Rapid."""
from requests import get, exceptions
from dotenv import load_dotenv
from os import getenv
from urllib.parse import urlparse
import json
from fuzzywuzzy import fuzz
import inquirer

load_dotenv()


class APIError(Exception):
    """Describes an error triggered by a failing API call."""

    def __init__(self, message: str, code: int = 500):
        """Creates a new APIError instance."""
        self.message = message
        self.code = code



def get_tennis_tours(url:str, headers:dict) -> dict:
    """Returns the tennis tours - ATP and WTA with a season_id in the keys."""
    response = get(f"{url}/tours", headers=head)

    if response.status_code == 200:
        result = response.json()

        return result["results"]
    
    if response.status_code == 400:
        raise APIError("Unable to find URL.",
                        response.status_code)
    
    if response.status_code == 500:
        raise APIError("Unable to connect to server.", response.status_code)

def choose_tours() -> str:
    """Returns a chosen tour from the list."""

    tours = {"ATP", "WTA"}
    
    max_attempts = 3

    attempts = 0

    while attempts < max_attempts:
        try:

            tour_name = input("Please insert a tennis tour: ").strip().upper()
            if not tour_name.isalpha():
                raise TypeError ("Wrong formatting!")
            
            if fuzz.partial_token_sort_ratio(tour_name, "ATP Tour") > 60:
                print("You've chosen ATP")
                return "ATP"
            
            elif fuzz.partial_token_sort_ratio(tour_name, "WTA Tour") > 60:
                print("You've chosen WTA")
                return "WTA"
            
            else:
                print("Wrong name!")
        
        except EOFError as e:
            print(f"There has been an error - {e}")

        except TypeError as e:
            print(f"Wrong format - {e}")
    
        attempts += 1
    

    print("No tour was selected!")
    return None
            

def get_players(url:str, headers:dict, tour:str) -> dict:
    """Returns the list of players, from the WTA tour, or the ATP tour. Also creates a local copy on a json file."""

    response = get(f"{url}players/{tour}", headers=headers)


    if response.status_code == 200:
        result = response.json()
        if "results" in result:
            if "players" in result["results"]:
                if tour == "ATP":
                    with open("atp_players.json" , "w") as file:
                        json.dump(result["results"]["players"], file, indent=4)
                elif tour == "WTA":
                    with open("wta_players.json", "w") as file:
                        json.dump(result["results"]["players"], file, indent=4)
                
                return result["results"]["players"]
    
    if response.status_code == 400:
        return APIError("Unable to find URL.", response.status_code)
    
    if response.status_code == 500:
        return APIError("Unable to connect to server.", response.status_code)
    

def get_player_info(url:str, headers:dict, player_id:int) -> dict:
    """Returns the data for a particular player."""

    response = get(f"{url}player/{player_id}", headers=headers)


    if response.status_code == 200:
        print("yes")
        result = response.json()
        return result
    
    if 400 <= response.status_code < 500:
        return APIError("Unable to find URL", response.status_code)
    
    if response.status_code == 500:
        return APIError("Unable to connect to server.", response.status_code)


def map_player_id(players) -> dict:
    """Returns all the players, with an id assigned to them from the API."""
    players_with_id = {}

    for player in players:
        players_with_id[player["full_name"]] = player["id"]

    return players_with_id


def find_player_id(player_name:str, players) -> int:
    """Returns the player id using their name."""
    players = map_player_id(players)

    return players[player_name]


def get_player(players:list[dict]) -> list[str]:

    player_names = [player["full_name"] for player in players]


    max_attempts = 3

    attempts = 0

    while attempts < max_attempts:
        user_request = input("Please insert the player's name: ").strip().lower()
        attempts += 1

        if user_request.replace(" ", "").isalpha():
            user_request = user_request.lower()
            break
    
    found_players = []

    for name in player_names:
        percentage = fuzz.WRatio(user_request, name)
        if percentage > 70:
            found_players.append(name)
    
    if len(found_players) > 1:
        return choose_players_from_list(found_players)
    
    if len(found_players) == 1:
        return found_players[0]
    
    return None

    




def choose_players_from_list(found_players:list[str]) -> str:
    """Returns one player from a list of found players."""
    question = [
        inquirer.List(
            "player",
            message = "These are the found players, please select one:",
            choices = found_players
        ),
    ]

    try:
        answer = inquirer.prompt(question)

        if answer is None:
            print("No selection made. Exiting...")
            return None
        
        else:
            print(f"You selected {answer["player"]}")
            return answer["player"]
    
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")


    





    
if __name__ == "__main__":
    BASE_URL = "https://tennis-live-data.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": getenv("API_KEY"),
        "X-RapidAPI-Host": getenv("HOST")
    }

    tour = choose_tours()

    if tour:
        players = get_players(BASE_URL, headers, tour)
        if players:
            player = get_player(players)
            if player:
                player_id = find_player_id(player, players)
                player_info = get_player_info(BASE_URL, headers, player_id)

                print(player_info["results"])




    






    

    

    