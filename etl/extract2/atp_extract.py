"""This script will scrap ATP tennis players details. """

from bs4 import BeautifulSoup
from requests import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import time
import os
import json


def extract_players_links():
    """Returns all the links for all the players in the tour between ranking 1-300 during 2018-2024."""

    cut_off_dates = [
        "2018-04-16",
        "2019-04-15",
        "2020-03-16",
        "2021-04-12",
        "2022-04-18",
        "2023-04-17",
        "2024-04-15"
    ]

    years = []
    players = []

    for date in cut_off_dates:
        years.append(get_players_by_year(date))

    for year in years:
        for player in year:
            player_link = get_player_link(player)

            if player_link not in players:
                players.append(player_link)
    

    return players
    

    
    
    

    


def get_players_by_year(date:str):
    """Returns the divs for the players."""

    BASE_URL = f"https://www.atptour.com/en/rankings/singles?rankRange=0-300&dateWeek={date}"

    ua = UserAgent()

    headers = {
        "User-Agent": ua.random
    }
    response = get(BASE_URL, headers=headers)

    if response.status_code == 200:
        players_soup = BeautifulSoup(response.content, "html.parser")

        players_section = players_soup.find(
            "table", class_="mega-table desktop-table non-live")
        
        players_divs = players_section.find_all("tr", class_="lower-row")

        return players_divs



def get_player_link(row):
    """Returns the name and the player with its respective link."""

    row.find("a")

    a_tag = row.find("a")

    if a_tag:
        name = a_tag.text.strip()
        ref = a_tag.get("href")

        return {name : ref}

def get_players_info(players_list):
    """Returns all players info."""
    players = []

    for player in players_list:
        players.append(get_player_info(player))
    
    return players


def get_player_info(player_dict):

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    
    link = list(player_dict.values())[0]
    name = list(player_dict.keys())[0]

    BASE_URL = f"https://www.atptour.com/{link}"

    driver.get(BASE_URL)
    time.sleep(5)
    button = driver.find_element(By.ID, "onetrust-reject-all-handler")
    button.click()
    time.sleep(3)
    website_source = driver.page_source

    player_soup = BeautifulSoup(website_source, "html.parser")
    if player_soup:
        details = player_soup.find("div", class_="personal_details")
        content = details.find("div", class_="pd_content")
        sections = content.find_all("li")
        filtered_li = [li for li in sections  if "socialLink.SocialId" not in str(li) or "Follow player" not in str(li)]
        player_details = {}

        for element in filtered_li:
            if not element.find("div", class_="social") and not element.find("a"):
                detail = element.find_all("span")
                player_details[detail[0].text.strip()] = detail[1].text.strip()
        
        driver.quit()
        

        return {name:player_details}


def save_player_details(player_details):
    combined_details = {}
    for player in player_details:
        combined_details.update(player)

    with open("players_details.json", "w") as json_file:
        json.dump(combined_details, json_file, indent=4)

        

        

        


            


        
        





    





if __name__ == "__main__":
    players_links = extract_players_links()
    players_details = get_players_info(players_links)
    save_player_details(players_details)

