import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

st.set_page_config(page_title="TAURON Liga - Milestone Checker", page_icon="🏐", layout="wide")

st.title("🏐 TAURON Liga – Skaner Milestones")
st.write("Wybierz tryb działania aplikacji poniżej:")

POINT_STEP, POINT_MARGIN = 500, 35
BLOCK_STEP, BLOCK_MARGIN = 100, 10
ACE_STEP, ACE_MARGIN = 100, 10

# Baza klubów do wyboru ręcznego
TEAMS_DB = {
    "Developres Rzeszów": "https://www.tauronliga.pl/teams/id/11.html",
    "BKS Bostik ZGO Bielsko-Biała": "https://www.tauronliga.pl/teams/id/12.html",
    "ŁKS Commercecon Łódź": "https://www.tauronliga.pl/teams/id/8.html",
    "Grot Budowlani Łódź": "https://www.tauronliga.pl/teams/id/14.html",
    "UNI Opole": "https://www.tauronliga.pl/teams/id/24.html",
    "Grupa Azoty Chemik Police": "https://www.tauronliga.pl/teams/id/19.html"
}

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.tauronliga.pl/'
    }

def get_todays_teams():
    teams_dict = {}
    schedule_url = "https://www.tauronliga.pl/games/tour/53.html"
    
    try:
        res = requests.get(schedule_url, headers=get_headers(), timeout=10)
        if res.status_code != 200:
            return {}
            
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if "/teams/id/" in href:
                full_url = href if href.startswith("http") else f"https://www.tauronliga.pl{href}"
                team_name = a.get_text(strip=True)
                if team_name and len(team_name) > 2:
                    teams_dict[team_name] = full_url
    except Exception as e:
        st.error(f"Nie udało się pobrać terminarza: {e}")
        
    return teams_dict

def get_player_career_stats(player_url):
    try:
        res = requests.get(player_url, headers=get_headers(), timeout=5)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, 'html.parser')
        pts, aces, blk = 0, 0, 0

        for row in soup.find_all(['tr', 'li', 'div']):
            text = " ".join(row.get_text(separator=" ", strip=True).split())
            
            if "Liczba pkt zdobytych w lidze" in text:
                numbers = re.findall(r'\d+', text)
                if numbers: 
                    pts = int(numbers[-1])
            if "Liczba asów" in text:
                numbers = re.findall(r'\d+', text)
                if numbers: 
                    aces = int(numbers[-1])
            if "Liczba pkt z bloków" in text:
                numbers = re.findall(r'\d+', text)
                if numbers: 
                    blk = int(numbers[-1])

        return {"pts": pts, "aces": aces, "blk": blk}
    except Exception:
        return None

def check_milestones(pts, aces, blk):
    alerts = []
    if pts > 0:
        next_pts = ((pts // POINT_STEP) + 1) * POINT_STEP
        needed = next_pts - pts
        if 0 < needed <= POINT_MARGIN:
            alerts.append(f"🎯 **PUNKTY
