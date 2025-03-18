import asyncio
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import json
import os
import random
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import time

# Other functions remain the same as in the previous version

async def load_match_webpage(year: int, match_number: str):
    """Accesses the webpage of a Roland Garros match and scrapes the data."""
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)

    try:
        BASE_URL = "https://www.rolandgarros.com/en-us/matches/"
        response = f"{BASE_URL}{year}/SM{match_number}"

        driver.get(response)

        try:
            button = driver.find_element(By.ID, "popin_tc_privacy_button")
            button.click()
            await asyncio.sleep(3)
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
            await asyncio.sleep(3)

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
            await asyncio.sleep(3)

            rally_stats_button = driver.find_element(By.XPATH, "//*[@id='RallyAnalysis']/section/footer/div")
            rally_stats_button.click()
            await asyncio.sleep(3)

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


async def get_year_data(max_retries=5, retry_delay=3):
    """
    Retrieve match data with retry logic, handle errors, and save yearly data to individual JSON files.
    """
    years = [num for num in range(2018,2025)]
    matches = [f"{match_num:03d}" for match_num in range(1, 128)]

    for year in years:
        matches_dict = {}

        for match in matches:
            match_code = f"SM{match}"
            
            success = False
            attempts = 0
            
            while not success and attempts < max_retries:
                try:
                    print(f"Fetching {match_code} for {year} (Attempt {attempts + 1}/{max_retries})...")
                    
                    match_data = await load_match_webpage(year, match)
                    
                    matches_dict[match_code] = match_data
                    print(f"✅ Successfully retrieved {match_code} for {year}")
                    
                    success = True

                except Exception as e:
                    attempts += 1
                    print(f"❌ Error fetching {match_code}: {e}")
                    
                    if attempts < max_retries:
                        wait_time = retry_delay + random.uniform(0, 2)
                        print(f"Retrying in {wait_time:.2f} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"⚠️ Max retries reached. Skipping {match_code}")
                        matches_dict[match_code] = {"error": str(e)}

        year_filename = f"RG_{year}.json"
        save_to_json(matches_dict, year_filename)
        print(f"📁 Data for {year} saved to {year_filename}")


def save_to_json(data, filename):
    """Save dictionary to a JSON file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Data saved to {filename}")


if __name__ == "__main__":
    asyncio.run(get_year_data())
