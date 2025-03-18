"""This script will retrieve data from Roland Garros website."""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from collections import defaultdict

def load_match_webpage(year:int, match_number:str):
    """This function simulates acccessing the webpage of a Roland garros match."""
    options = Options()
    # options.add_argument("--headless=new")
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
    player_1 = get_player_name(soup_stats, "team team1")
    player_2 = get_player_name(soup_stats, "team team2")

    match_stats = get_match_stats(soup_stats)
    match_stats_dict = {}
    player_stats = {}
    for match in match_stats:
        section_title = match.find("div", {"class": "rfk-heading"}).text.strip().upper()
        match_stats_dict[section_title] = get_section_match_stats(match)[0]
        player_stats[player_1] = match_stats_dict
        match_stats_dict[section_title] = get_section_match_stats(match)[1]
        player_stats[player_2] = match_stats_dict   
    print(player_stats)
    

    back_stats_button = driver.find_element(By.XPATH, "//*[@id='MatchStats']/section/header/button")
    back_stats_button.click()
    time.sleep(5)
    rally_stats_button = driver.find_element(By.XPATH, "//*[@id='RallyAnalysis']/section/footer/div")
    rally_stats_button.click()
    time.sleep(5)
    rallys_websource = driver.page_source
    rally_stats = BeautifulSoup(rallys_websource, "html.parser")
    get_section_rally_stats(rally_stats)
    time.sleep(60)
    # back_rally_button = driver.find_element(By.XPATH, "//*[@id='RallyAnalysis']/section/header/button")
    # back_rally_button.click()
    # driver.quit()

    return driver



def get_player_name(soup_name, class_name) -> str:
    """Returns player name by extracting it using the class name."""
    player = soup_name.find("div", class_=class_name)
    player_details = player.find("div", class_="player-details")
    player_data= player_details.find("span", class_="name")
    player_name = player_data.find('a', {'class': 'player-details-anchor'}).text.strip()


    return player_name

def get_match_stats(soup_name):
    """Returns all the sections with important stats from the match. Service, breakpoints, receiving points, points breakdown."""
    
    match_stats = soup_name.find_all("div", class_="rfk-stat-section")
    
    return match_stats

def get_section_match_stats(soup_name):
    player_1_data = {}
    player_2_data = {}
    subsections = soup_name.find_all("div", class_="rfk-statTileWrapper")
    for subsection in subsections:
        subsection_title = subsection.find("div",  {"class": "rfk-labelbold rfk-cursorNone"}).text.strip()

        player_1 = ""
        player_2 = ""
        if subsection.find("div", class_="rfk-label rfk-player1 rfk-non-speed"):
            player_1 = subsection.find("div", {"class": "rfk-label rfk-player1 rfk-non-speed"}).text.strip()
            player_1_data[subsection_title] = player_1
        
        if subsection.find("div", class_="rfk-labelBold rfk-player1 rfk-non-speed"):
            player_1 = subsection.find("div", {"class": "rfk-labelBold rfk-player1 rfk-non-speed"}).text.strip()
            player_1_data[subsection_title] = player_1

        if subsection.find("div", class_="rfk-label rfk-player2 rfk-non-speed"):
            player_2 = subsection.find("div", {"class": "rfk-label rfk-player2 rfk-non-speed"}).text.strip()
            player_2_data[subsection_title] = player_2

        if subsection.find("div", class_="rfk-labelBold rfk-player2 rfk-non-speed"):
            player_2 = subsection.find("div", {"class": "rfk-labelBold rfk-player2 rfk-non-speed"}).text.strip()
            player_2_data[subsection_title] = player_2
        
        if subsection.find("div", class_="rfk-speedDiv1"):
            player_1 = subsection.find("div", {"class": "rfk-speedDiv1"}).text.strip()
            player_1_data[subsection_title] = player_1
        
        if subsection.find("div", class_="rfk-speedDiv2"):
            player_2 = subsection.find("div", {"class": "rfk-speedDiv2"}).text.strip()
            player_2_data[subsection_title] = player_2

    return [player_1_data, player_2_data]


def get_section_rally_stats(soup_name):
    """Returns stats from the rally section on the webpage."""
    player_1_data = {}
    player_2_data = {}
    total_points_won = soup_name.find("div", class_= "label label-team1")
    print(total_points_won)



    
    


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