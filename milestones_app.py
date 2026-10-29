import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

st.set_page_config(page_title="TAURON Liga - Milestone Checker", page_icon="🏐", layout="wide")

st.title("🏐 TAURON Liga – Skaner Meczów wg Daty")
st.write("Wybierz datę, aby automatycznie wykryć drużyny grające tego dnia i sprawdzić ich składy.")

POINT_STEP, POINT_MARGIN = 500, 35
BLOCK_STEP, BLOCK_MARGIN = 100, 10
ACE_STEP, ACE_MARGIN = 100, 10

TEAMS_DB = {
    "Indykpol AZS Olsztyn": "https://www.tauronliga.pl/teams/id/24.html",
    "Asseco Resovia Rzeszów": "https://www.tauronliga.pl/teams/id/11.html",
    "Grupa Azoty ZAKSA Kędzierzyn-Koźle": "https://www.tauronliga.pl/teams/id/12.html",
    "Trefl Gdańsk": "https://www.tauronliga.pl/teams/id/14.html",
    "Projekt Warszawa": "https://www.tauronliga.pl/teams/id/19.html",
    "Jastrzębski Węgiel": "https://www.tauronliga.pl/teams/id/8.html"
}

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.tauronliga.pl/'
    }

def get_teams_for_date(target_date):
    teams_dict = {}
    date_str_dot = target_date.strftime("%d.%m.%Y")
    date_str_short = target_date.strftime("%d.%m")
    
    schedule_url = "https://www.tauronliga.pl/games/tour/53.html"
    
    try:
        res = requests.get(schedule_url, headers=get_headers(), timeout=10)
        if res.status_code != 200:
            return {}
            
        soup = BeautifulSoup(res.text, 'html.parser')
        elements = soup.find_all(['tr', 'div', 'section', 'article'])
        
        for el in elements:
            text = el.get_text()
            if date_str_dot in text or date_str_short in text:
                for a in el.find_all('a', href=True):
                    href = a['href']
                    if "/teams/id/" in href:
                        full_url = href if href.startswith("http") else f"https://www.tauronliga.pl{href}"
                        team_name = a.get_text(strip=True)
                        if team_name and len(team_name) > 2:
                            teams_dict[team_name] = full_url
                            
        if not teams_dict:
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "/teams/id/" in href:
                    full_url = href if href.startswith("http") else f"https://www.tauronliga.pl{href}"
                    team_name = a.get_text(strip=True)
                    if team_name and len(team_name) > 2:
                        teams_dict[team_name] = full_url
                        
    except Exception as e:
        st.error(f"Błąd podczas pobierania terminarza: {e}")
        
    return teams_dict

def get_player_career_stats(player_url):
    try:
        res = requests.get(player_url, headers=get_headers(), timeout=5)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, 'html.parser')
        pts, aces, blk = 0, 0, 0

        for row in soup.find
