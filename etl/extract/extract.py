"""This script will extract live data from Rapid."""
from requests import get, exceptions
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class APIError(Exception):
    """Describes an error triggered by a failing API call."""

    def __init__(self, message: str, code: int = 500):
        """Creates a new APIError instance."""
        self.message = message
        self.code = code



def get_atp_tours(url:str, head:dict) -> dict:

    response = get(f"{url}/tours", headers=head)

    if response.status_code == 200:
        return response.json()
    
    if response.status_code == 400:
        raise APIError("Unable to find URL.",
                        response.status_code)
    
    if response.status_code == 500:
        raise APIError("Unable to connect to server.", response.status_code)


    


if __name__ == "__main__":
    BASE_URL = "https://tennis-live-data.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": getenv("API_KEY"),
        "X-RapidAPI-Host": getenv("HOST")
    }

    print(get_atp_tours(BASE_URL, headers))

    