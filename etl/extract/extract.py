"""This script will extract live data from Rapid."""
from requests import get, exceptions
from dotenv import load_dotenv
from os import getenv
from urllib.parse import urlparse
import json

load_dotenv()


class APIError(Exception):
    """Describes an error triggered by a failing API call."""

    def __init__(self, message: str, code: int = 500):
        """Creates a new APIError instance."""
        self.message = message
        self.code = code



def get_tennis_tours(url:str, headers:dict) -> dict:

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

    tours = ["ATP", "WTA"]
    
    max_attempts = 3

    for _ in range(max_attempts):
        tour_name = input("Please insert a tennis tour: ")
        if tour_name.isalpha():
            tour_name = tour_name.upper()
            if tour_name in tours:
                return tour_name
            else:
                print("Enter a valid tour name!")
        else:
            print("Enter a valid tour name!")

    
    return "No Tour was selected!"
            
    

    
    


def get_players_locally(url:str, headers:dict, tour:str) -> dict:

    response = get(f"{url}/players/{tour}", headers=headers)

    if response.status_code == 200:
        result = response.json()
        if "results" in result:
            if "players" in result["results"]:
                with open("players.json" , "w") as file:
                    json.dump(result["results"]["players"], file, indent=4)
    
    if response.status_code == 400:
        return APIError("Unable to find URL.", response.status_code)
    
    if response.status_code == 500:
        return APIError("Unable to connect to server.", response.status_code)
    

def get_players(url:str, headers:dict, player_id:int) -> dict:

    response = get(f"{url}/")
    


    


if __name__ == "__main__":
    BASE_URL = "https://tennis-live-data.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": getenv("API_KEY"),
        "X-RapidAPI-Host": getenv("HOST")
    }

    # tours = get_tennis_tours(BASE_URL, head=headers)

    # for tour in tours:
    #     print(tour)

    chosen_tour = choose_tours()

    tennis_players = get_players_locally(BASE_URL, headers, chosen_tour)

    print(tennis_players)

    

    