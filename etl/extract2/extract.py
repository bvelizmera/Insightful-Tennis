"""This script will retrieve data from Roland Garros website."""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import json
import os
import time
import random


def load_match_webpage(year:int, match_number:str):
    """This function simulates acccessing the webpage of a Roland garros match."""
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
    time.sleep(5)
    score_websource = driver.page_source
    score_soup = BeautifulSoup(score_websource, "html.parser")
    player_1 = get_player_name(score_soup, "pl-container team-a")
    player_2 = get_player_name(score_soup, "pl-container team-b")
    winner = get_match_winner(score_soup)
    score = get_overall_score(score_soup)
    formatted_score = get_score_into_final_format(score)
    stats_button = driver.find_element(By.XPATH, "//*[@id='MatchStats']/section/footer/div")
    stats_button.click()
    time.sleep(5)
    stats_websource = driver.page_source
    soup_stats = BeautifulSoup(stats_websource, "html.parser")
    match_stats = get_match_stats(soup_stats)
    match_stats_dict = {}
    player_stats = {}
    for match in match_stats:
        section_title = match.find("div", {"class": "rfk-heading"}).text.strip().upper()
        match_stats_dict[section_title] = get_section_match_stats(match)[0]
        player_stats[player_1] = match_stats_dict
        match_stats_dict[section_title] = get_section_match_stats(match)[1]
        player_stats[player_2] = match_stats_dict

    back_stats_button = driver.find_element(By.XPATH, "//*[@id='MatchStats']/section/header/button")
    back_stats_button.click()
    time.sleep(5)
    rally_stats_button = driver.find_element(By.XPATH, "//*[@id='RallyAnalysis']/section/footer/div")
    rally_stats_button.click()
    time.sleep(5)
    rallys_websource = driver.page_source
    rally_stats = BeautifulSoup(rallys_websource, "html.parser")
    player_1_stats = player_stats[player_1].copy()
    player_2_stats = player_stats[player_2].copy()
    rally_points_distribution = get_section_rally_stats(rally_stats)
    player_1_stats["RALLY POINTS DISTRIBUTION"] = rally_points_distribution[0]
    player_1_stats["Games"] = score[0]
    if player_1 == winner:
        player_1_stats["Winner"] = True
    
    else:
        player_1_stats["Winner"] = False

    player_2_stats["RALLY POINTS DISTRIBUTION"] = rally_points_distribution[1]
    player_2_stats["Games"] = score[1]
    if player_2 == winner:
        player_2_stats["Winner"] = True
    
    else:
        player_2_stats["Winner"] = False

    player_stats_rallies = {}
    player_stats_rallies[player_1] = player_1_stats
    player_stats_rallies[player_2] = player_2_stats    

    driver.quit()
    
    return {"Score":formatted_score, "Details": player_stats_rallies}




def get_player_name(soup_name, class_name) -> str:
    """Returns player name by extracting it using the class name."""
    player = soup_name.find("div", class_= class_name)
    player_name = player.find("div", {"class": "player-name"}).text.strip()
    return player_name

def get_match_stats(soup_name):
    """Returns all the sections with important stats from the match. Service, breakpoints, receiving points, points breakdown."""
    
    match_stats = soup_name.find_all("div", class_="rfk-stat-section")
    
    return match_stats

def get_section_match_stats(soup_name):
    """Retrieves data from match stats."""
    player_1_data = {}
    player_2_data = {}
    subsections = soup_name.find_all("div", class_="rfk-statTileWrapper")
    for subsection in subsections:
        subsection_title = subsection.find("div",  {"class": "rfk-labelBold rfk-cursorNone"}).text.strip()

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
    player_1_data["Total Points Won"] = soup_name.find("span", {"class":"tile team1"}).text.strip()
    player_2_data["Total Points Won"] = soup_name.find("span", {"class":"tile team2"}).text.strip()

    rally_sections = soup_name.find("div", class_="rallies")

    subsections = rally_sections.find_all("div", {"class" : "rallyCard-wrapper undefined highligted"})

    for subsection in subsections:
        subsection_title = subsection.find("span", {"class" : "rally-name-label"}).text.strip()
        
        if subsection.find("span", class_="tile team1"):
            player_1_data[subsection_title] = subsection.find("span", {"class" : "tile team1"}).text.strip()
        
        if subsection.find("span", class_="tile team2"):
            player_2_data[subsection_title] = subsection.find("span", {"class" : "tile team2"}).text.strip()
    
    return [player_1_data, player_2_data]


def get_overall_score(soup_name):

    scores = soup_name.find_all("div", class_="result-content")

    p1_score = []
    p2_score = []


    for score in scores:

        if 'team-a-content' in score.get('class', []):
            p1_sets_div = score.find("div", class_="group-sets")

            p1_sets_results = p1_sets_div.find_all("div", class_="set")

            for p1_set in p1_sets_results:
                if "tie-break" in p1_set.get("class", []):
                    
                    set_score = f"{p1_set.contents[0].strip()} ({p1_set.contents[1].text.strip()})"
                    p1_score.append(set_score)
                
                else:
                    set_score = p1_set.text.strip()
                    p1_score.append(set_score)


        else:
            p2_sets_div = score.find("div", class_="group-sets")

            p2_sets_results = p2_sets_div.find_all("div", class_="set")

            for p2_set in p2_sets_results:
                if "tie-break" in p2_set.get("class", []):
                    
                    set_score = f"{p2_set.contents[0].strip()} ({p2_set.contents[1].text.strip()})"
                    p2_score.append(set_score)
                
                else:
                    set_score = p2_set.text.strip()
                    p2_score.append(set_score)
        
    
    return [p1_score, p2_score]

def get_match_winner(soup_name):
    
    players_soup = soup_name.find_all("div", class_="result-content")

    for player in players_soup:
        if "winner" in player.get("class", []):
            player_name = player.find("div", {"class": "player-name"}).text.strip()
    
    
    return player_name

def get_score_into_final_format(score:list) -> list:
    """Returns the score into a formatted list."""

  
    formatted_scores = [f"{s1}-{s2}" for s1, s2 in zip(*score)]

    return formatted_scores




def get_year_data(max_retries=5, retry_delay=3):
    """
    Retrieve match data with retry logic, handle errors, and save yearly data to individual JSON files.
    """
    years = [2018]  # Add your desired years here
    matches = [f"{match_num:03d}" for match_num in range(1, 128)]

    for year in years:
        matches_dict = {}

        for match in matches:
            match_code = f"SM{match}"
            
            # Retry logic
            success = False
            attempts = 0
            
            while not success and attempts < max_retries:
                try:
                    print(f"Fetching {match_code} for {year} (Attempt {attempts + 1}/{max_retries})...")
                    
                    # Attempt to load match data
                    match_data = load_match_webpage(year, match)
                    
                    # If successful, store the data
                    matches_dict[match_code] = match_data
                    print(f"✅ Successfully retrieved {match_code} for {year}")
                    
                    success = True  # Exit retry loop after successful fetch

                except Exception as e:
                    attempts += 1
                    print(f"❌ Error fetching {match_code}: {e}")
                    
                    if attempts < max_retries:
                        wait_time = retry_delay + random.uniform(0, 2)  # Add jitter for retry
                        print(f"Retrying in {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"⚠️ Max retries reached. Skipping {match_code}")
                        matches_dict[match_code] = {"error": str(e)}

        # Save the year's data into its own JSON file
        year_filename = f"RG_{year}.json"
        save_to_json(matches_dict, year_filename)
        print(f"📁 Data for {year} saved to {year_filename}")


def save_to_json(data, filename):
    """Save dictionary to a JSON file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Data saved to {filename}")


    
if __name__ == "__main__":
    # get_year_data()
    print(load_match_webpage(2019, "001"))
