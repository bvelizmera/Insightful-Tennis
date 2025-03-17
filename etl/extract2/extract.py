"""This script will retrieve data from Roland Garros website."""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def load_match_webpage(year:int, match_number:str):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    BASE_URL = "https://www.rolandgarros.com/en-us/matches/"
    response = f"{BASE_URL}{year}/SM{match_number}"

    driver.get(response)
    button = driver.find_element(By.ID, "popin_tc_privacy_button")
    button.click()
    time.sleep(3)
    stats_button = driver.find_element(By.XPATH, "//*[@id='MatchStats']/section/footer/div")
    stats_button.click()
    time.sleep(2)
    stats_websource = driver.page_source
    soup_stats = BeautifulSoup(stats_websource, "html.parser")
    players = {}
    players["player_1"] = get_player_name(soup_stats, "team team1")
    players["player_2"] = get_player_name(soup_stats, "team team2")

    match_stats = get_match_stats(soup_stats)
    for match in match_stats:
        print(get_section_match_stats(match))
    

    # back_stats_button = driver.find_element(By.XPATH, "//*[@id='MatchStats']/section/header/button")
    # back_stats_button.click()
    # time.sleep(5)
    # rally_stats_button = driver.find_element(By.XPATH, "//*[@id='RallyAnalysis']/section/footer/div")
    # rally_stats_button.click()
    # time.sleep(5)
    # back_rally_button = driver.find_element(By.XPATH, "//*[@id='RallyAnalysis']/section/header/button")
    # back_rally_button.click()
    driver.quit()

    return driver



def get_player_name(soup_name, class_name) -> str:
    player = soup_name.find("div", class_=class_name)
    player_details = player.find("div", class_="player-details")
    player_data= player_details.find("span", class_="name")
    player_name = player_data.find('a', {'class': 'player-details-anchor'}).text.strip()


    return player_name

def get_match_stats(soup_name):
    match_stats = soup_name.find_all("div", class_="rfk-stat-section")
    return match_stats

def get_section_match_stats(soup_name):
    section_name = soup_name.find("div", {"class": "rfk-heading"}).text.strip()
    return section_name


    




# def get_match_data_atp_infosys_stats(year:int, match_number:str):
#     """Returns connection to a specific match."""
#     BASE_URL = "https://www.rolandgarros.com/en-us/matches/"
#     response = requests.get(f"{BASE_URL}{year}/SM{match_number}")

#     if response.status_code == 200:
#         found_matches = 0
#         soup = BeautifulSoup(response.text, "html.parser")
#         if soup.find("h3", class_="error-view-message"):
#             return False
        
#         match_data = soup.find("div", attrs={"data-v-e932b888": True})

#         if match_data:
#             return match_data

            

        

        
    
    if 400 <= response.status_code < 500:
        print("No")

def get_year_data():
    found_matches = 0

    years = [number for number in range(2018, 2020)]
    matches = [f"{match_num:03d}" for match_num in range(1, 128)]

    for year in years:
        for match in matches:
            load_match_webpage(year, match)
            found_matches += 1
    
    return found_matches
            
    


    
if __name__ == "__main__":
    # match_data = get_match_data_atp_infosys_stats(2018, "127")
    # match_stats = match_data.find("div", class_="rfk-stat-section")
    # get_year_data()

    load_match_webpage(2018,"001")
