"""This script will retrieve data from Roland Garros website."""

import requests
from bs4 import BeautifulSoup
import selenium

def load_match_stats_page(match_url:str)

def get_match_data_atp_infosys_stats(year:int, match_number:str):
    """Returns connection to a specific match."""
    BASE_URL = "https://www.rolandgarros.com/en-us/matches/"
    response = requests.get(f"{BASE_URL}{year}/SM{match_number}")

    if response.status_code == 200:
        found_matches = 0
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("h3", class_="error-view-message"):
            return False
        
        match_data = soup.find("div", attrs={"data-v-e932b888": True})

        if match_data:
            return match_data

            

        

        
    
    if 400 <= response.status_code < 500:
        print("No")

def get_year_data():
    found_matches = 0

    years = [number for number in range(2018, 2019)]
    matches = [f"{match_num:03d}" for match_num in range(1, 128)]

    for year in years:
        for match in matches:
            if get_match_data_atp(year, match):
                found_matches += 1
    
    return found_matches
            
    


    
if __name__ == "__main__":
    match_data = get_match_data_atp_infosys_stats(2018, "127")
    match_stats = match_data.find("div", class_="rfk-stat-section")

    print(match_stats)