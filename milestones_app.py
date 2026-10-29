import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

st.set_page_config(page_title="TAURON Liga - Milestone Checker", page_icon="🏐", layout="wide")

st.title("🏐 TAURON Liga – Skaner Meczów wg Daty")
st.write("Wybierz datę. Aplikacja spróbuje automatycznie dopasować drużyny, a w razie potrzeby możesz je łatwo zmienić poniżej.")

POINT_STEP, POINT_MARGIN = 500, 35
BLOCK_STEP, BLOCK_MARGIN = 100, 10
ACE_STEP, ACE_MARGIN = 100, 10

# Pełna baza drużyn jako bezpieczny punkt wyjścia / awarię
ALL_TEAMS = {
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
    """Wchodzi na stronę terminarza i próbuje wyciągnąć drużyny z wybranej daty"""
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
                if numbers: pts = int(numbers[-1])
            if "Liczba asów" in text:
                numbers = re.findall(r'\d+', text)
                if numbers: aces = int(numbers[-1])
            if "Liczba pkt z bloków" in text:
                numbers = re.findall(r'\d+', text)
                if numbers: blk = int(numbers[-1])

        return {"pts": pts, "aces": aces, "blk": blk}
    except Exception:
        return None

def check_milestones(pts, aces, blk):
    alerts = []
    if pts > 0:
        next_pts = ((pts // POINT_STEP) + 1) * POINT_STEP
        needed = next_pts - pts
        if 0 < needed <= POINT_MARGIN:
            alerts.append(f"🎯 **PUNKTY**: {pts} pkt -> Brakuje **{needed}** do progu {next_pts}")
            
    if aces > 0:
        next_aces = ((aces // ACE_STEP) + 1) * ACE_STEP
        needed = next_aces - aces
        if 0 < needed <= ACE_MARGIN:
            alerts.append(f"💣 **ASY**: {aces} asów -> Brakuje **{needed}** do progu {next_aces}")
            
    if blk > 0:
        next_blk = ((blk // BLOCK_STEP) + 1) * BLOCK_STEP
        needed = next_blk - blk
        if 0 < needed <= BLOCK_MARGIN:
            alerts.append(f"🧱 **BLOKI**: {blk} bloków -> Brakuje **{needed}** do progu {next_blk}")
    return alerts

# 1. Wybór daty przez użytkownika
selected_date = st.date_input("Wybierz datę meczów do analizy:", datetime.now())

# 2. Automatyczne wykrywanie drużyn dla danej daty
detected_teams = get_teams_for_date(selected_date)

# Jeśli automatyczne wykrycie nic nie zwróci dla tej daty, podpowiadamy domyślne z bazy
default_selection = list(detected_teams.keys()) if detected_teams else list(ALL_TEAMS.keys())[:2]

# 3. Pole wyboru (multiselect) – daje 100% kontroli i eliminuje problemy z niedopasowaniem daty
selected_team_names = st.multiselect(
    "Wykryte drużyny (możesz je dowolnie zmienić lub dodać inne z listy):",
    options=list(ALL_TEAMS.keys()),
    default=default_selection
)

# 4. Przycisk startowy skanowania
if st.button("🔍 Skanuj wybrane drużyny"):
    teams_found = {name: ALL_TEAMS[name] for name in selected_team_names if name in ALL_TEAMS}
    
    if not teams_found:
        st.warning("Nie wybrano żadnych drużyn do skanowania.")
    else:
        st.success(f"Analizuję drużyny: {', '.join(teams_found.keys())}")
        
        total_alerts_found = 0
        overall_progress = st.progress(0)
        status_box = st.empty()
        
        teams_list = list(teams_found.items())
        teams_count = len(teams_list)
        
        for t_idx, (team_name, team_url) in enumerate(teams_list):
            status_box.text(f"Analizuję skład drużyny ({t_idx+1}/{teams_count}): {team_name}...")
            
            try:
                res = requests.get(team_url, headers=get_headers(), timeout=5)
                if res.status_code != 200:
                    continue
                
                soup = BeautifulSoup(res.text, 'html.parser')
                player_links = []
                seen_urls = set()
                
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if "/players/id/" in href and "/tour/" in href:
                        full_url = href if href.startswith("http") else f"https://www.tauronliga.pl{href}"
                        name = a.get_text(strip=True)
                        if name and full_url not in seen_urls:
                            seen_urls.add(full_url)
                            player_links.append({"name": name, "url": full_url})
                
                if player_links:
                    st.subheader(f"🛡️ {team_name}")
                    for player in player_links:
                        stats = get_player_career_stats(player["url"])
                        if stats:
                            alerts = check_milestones(stats["pts"], stats["aces"], stats["blk"])
                            if alerts:
                                total_alerts_found += 1
                                st.success(f"👤 **{player['name']}**")
                                for alert in alerts:
                                    st.markdown(f"    • {alert}")
            
            except Exception as e:
                st.error(f"Błąd przy drużynie {team_name}: {e}")
                
            overall_progress.progress((t_idx + 1) / teams_count)
            
        status_box.text("Skanowanie zakończone!")
        if total_alerts_found == 0:
            st.info("Przeskanowano składy wybranych drużyn – żaden zawodnik nie znajduje się w strefie marginesu.")
        else:
            st.balloons()
