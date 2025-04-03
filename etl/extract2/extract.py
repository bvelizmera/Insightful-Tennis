"""This script will retrieve data from Roland Garros website."""
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
import random
from selenium.common.exceptions import NoSuchElementException


def load_match_webpage(year: int, match_number: str):
    """Accesses the webpage of a Roland Garros match and scrapes the data."""
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)

    try:
        BASE_URL = "https://www.rolandgarros.com/en-us/matches/"
        response = f"{BASE_URL}{year}/SD{match_number}"

        driver.get(response)


        try:
            button = driver.find_element(By.ID, "popin_tc_privacy_button")
            button.click()
            time.sleep(3)
        except NoSuchElementException:
            print("⚠️ Privacy button not found, continuing...")

        score_websource = driver.page_source
        score_soup = BeautifulSoup(score_websource, "html.parser")
        player_1 = get_player_name(score_soup, "pl-container team-a")
        player_2 = get_player_name(score_soup, "pl-container team-b")
        winner = get_match_winner(score_soup)
        score = get_overall_score(score_soup)
        formatted_score = get_score_into_final_format(score)

        # Initialize player stats with score and winner data
        player_stats = {
            player_1: {
                "Games": score[0],
                "Winner": (player_1 == winner)
            },
            player_2: {
                "Games": score[1],
                "Winner": (player_2 == winner)
            }
        }

        try:
            stats_button = driver.find_element(By.XPATH, "//*[@id='MatchStats']/section/footer/div")
            stats_button.click()
            time.sleep(3)

            stats_websource = driver.page_source
            soup_stats = BeautifulSoup(stats_websource, "html.parser")
            match_stats = get_match_stats(soup_stats)

            # Add match stats to the player stats
            for match in match_stats:
                section_title = match.find("div", {"class": "rfk-heading"}).text.strip().upper()
                player_stats[player_1][section_title] = get_section_match_stats(match)[0]
                player_stats[player_2][section_title] = get_section_match_stats(match)[1]

        except NoSuchElementException:
            print("⚠️ Stats button not found, skipping stats...")

        try:
            back_stats_button = driver.find_element(By.XPATH, "//*[@id='MatchStats']/section/header/button")
            back_stats_button.click()
            time.sleep(3)

            rally_stats_button = driver.find_element(By.XPATH, "//*[@id='RallyAnalysis']/section/footer/div")
            rally_stats_button.click()
            time.sleep(3)

            rallys_websource = driver.page_source
            rally_stats = BeautifulSoup(rallys_websource, "html.parser")

            rally_points_distribution = get_section_rally_stats(rally_stats)


            player_stats[player_1]["RALLY POINTS DISTRIBUTION"] = rally_points_distribution[0]
            player_stats[player_2]["RALLY POINTS DISTRIBUTION"] = rally_points_distribution[1]

        except NoSuchElementException:
            print("⚠️ Rally stats button not found, skipping rally stats...")

        finally:
            driver.quit()

        return {"Score": formatted_score, "Details": player_stats}

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        driver.quit()
        return {"error": str(e)}





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
        if subsection.find("div",  class_= "rfk-labelbold rfk-cursorNone"):
            subsection_title = subsection.find("div",  {"class": "rfk-labelbold rfk-cursorNone"}).text.strip()

        if subsection.find("div", class_= "rfk-labelbold rfk-cursor"):
            subsection_title = subsection.find("div",  {"class": "rfk-labelbold rfk-cursor"}).text.strip()

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
    years = [num for num in range(2018,2025)]
    matches = [f"{match_num:03d}" for match_num in range(1, 128)]

    for year in years:
        matches_dict = {}

        for match in matches:
            match_code = f"SD{match}"
            
            success = False
            attempts = 0
            
            while not success and attempts < max_retries:
                try:
                    print(f"Fetching {match_code} for {year} (Attempt {attempts + 1}/{max_retries})...")
                    
                    match_data = load_match_webpage(year, match)
                    

                    matches_dict[match_code] = match_data
                    print(f"✅ Successfully retrieved {match_code} for {year}")
                    
                    success = True

                except Exception as e:
                    attempts += 1
                    print(f"❌ Error fetching {match_code}: {e}")
                    
                    if attempts < max_retries:
                        wait_time = retry_delay + random.uniform(0, 2)
                        print(f"Retrying in {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"⚠️ Max retries reached. Skipping {match_code}")
                        matches_dict[match_code] = {"error": str(e)}

        year_filename = f"RG_WTA_{year}.json"
        save_to_json(matches_dict, year_filename)
        print(f"📁 Data for {year} saved to {year_filename}")


def save_to_json(data, filename):
    """Save dictionary to a JSON file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Data saved to {filename}")

def rounds_mapping():
    tournament_map = {
    "Final": ["SM001"],
    "Semifinals": ["SM002", "SM003"],
    "Quarterfinals": ["SM004", "SM005", "SM006", "SM007"],
    "Round of 16": [
        "SM008", "SM009", "SM010", "SM011",
        "SM012", "SM013", "SM014", "SM015"
    ],
    "Round of 32": [
        "SM016", "SM017", "SM018", "SM019",
        "SM020", "SM021", "SM022", "SM023",
        "SM024", "SM025", "SM026", "SM027",
        "SM028", "SM029", "SM030", "SM031"
    ],
    "Round of 64": [
        "SM032", "SM033", "SM034", "SM035",
        "SM036", "SM037", "SM038", "SM039",
        "SM040", "SM041", "SM042", "SM043",
        "SM044", "SM045", "SM046", "SM047",
        "SM048", "SM049", "SM050", "SM051",
        "SM052", "SM053", "SM054", "SM055",
        "SM056", "SM057", "SM058", "SM059",
        "SM060", "SM061", "SM062", "SM063"
    ],
    "Round of 128": [
        "SM064", "SM065", "SM066", "SM067",
        "SM068", "SM069", "SM070", "SM071",
        "SM072", "SM073", "SM074", "SM075",
        "SM076", "SM077", "SM078", "SM079",
        "SM080", "SM081", "SM082", "SM083",
        "SM084", "SM085", "SM086", "SM087",
        "SM088", "SM089", "SM090", "SM091",
        "SM092", "SM093", "SM094", "SM095",
        "SM096", "SM097", "SM098", "SM099",
        "SM100", "SM101", "SM102", "SM103",
        "SM104", "SM105", "SM106", "SM107",
        "SM108", "SM109", "SM110", "SM111",
        "SM112", "SM113", "SM114", "SM115",
        "SM116", "SM117", "SM118", "SM119",
        "SM120", "SM121", "SM122", "SM123",
        "SM124", "SM125", "SM126", "SM127"
    ]
}



    
if __name__ == "__main__":
    get_year_data()
