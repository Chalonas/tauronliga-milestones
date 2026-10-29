import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

st.set_page_config(page_title="TAURON Liga - Milestone Checker", page_icon="🏐", layout="wide")

st.title("🏐 TAURON Liga – Skaner Meczów i Milestones")
st.write("Wybierz drużyny grające w interesującym Cię dniu i uruchom szybkie skanowanie składów.")

POINT_STEP, POINT_MARGIN = 500, 35
BLOCK_STEP, BLOCK_MARGIN = 100, 10
ACE_STEP, ACE_MARGIN = 100, 10

# Pełna i stabilna baza drużyn TAURON Ligi
TEAMS_DB = {
    "Grupa Azoty Chemik Police": "https://www.tauronliga.pl/teams/id/1.html",
    "BKS Bostik ZGO Bielsko-Biała": "https://www.tauronliga.pl/teams/id/2.html",
    "Developres Rzeszów": "https://www.tauronliga.pl/teams/id/3.html",
    "ŁKS Commercecon Łódź": "https://www.tauronliga.pl/teams/id/4.html",
    "Grot Budowlani Łódź": "https://www.tauronliga.pl/teams/id/5.html",
    "MOYA Radomka Radom": "https://www.tauronliga.pl/teams/id/6.html",
    "Energa MKS Kalisz": "https://www.tauronliga.pl/teams/id/7.html",
    "ITA TOOLS Sties Mielec": "https://www.tauronliga.pl/teams/id/9.html",
    "UNI Opole": "https://www.tauronliga.pl/teams/id/10.html",
    "Metalkas Pałac Bydgoszcz": "https://www.tauronliga.pl/teams/id/12.html",
    "Sokół & Hagric Mogilno": "https://www.tauronliga.pl/teams/id/15.html",
    " #${team_name} ": "https://www.tauronliga.pl/teams/id/14.html" # placeholder w razie czego, ale użyjemy bezpiecznego słownika
}

# Poprawiony, czysty słownik z poprawnymi nazwami drużyn TAURON Ligi
TEAMS_DB = {
    "Developres Rzeszów": "https://www.tauronliga.pl/teams/id/3.html",
    "ŁKS Commercecon Łódź": "https://www.tauronliga.pl/teams/id/4.html",
    "Grot Budowlani Łódź": "https://www.tauronliga.pl/teams/id/5.html",
    "BKS Bostik ZGO Bielsko-Biała": "https://www.tauronliga.pl/teams/id/2.html",
    "Grupa Azoty Chemik Police": "https://www.tauronliga.pl/teams/id/1.html",
    "MOYA Radomka Radom": "https://www.tauronliga.pl/teams/id/6.html",
    "UNI Opole": "https://www.tauronliga.pl/teams/id/10.html",
    "ITA TOOLS Stal Mielec": "https://www.tauronliga.pl/teams/id/9.html",
    "Metalkas Pałac Bydgoszcz": "https://www.tauronliga.pl/teams/id/12.html",
    "Sokół & Hagric Mogilno": "https://www.tauronliga.pl/teams/id/15.html",
    "Energa MKS Kalisz": "https://www.tauronliga.pl/teams/id/7.html"
}

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.tauronliga.pl/'
    }

def get_player_career_stats(player_url):
    try:
        res = requests.get(player_url, headers=get_headers(), timeout=4)
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

# Wybór daty (informacyjnie dla użytkownika)
selected_date = st.date_input("Wybierz datę meczów:", datetime.now())

# Wybór drużyn z pełnej listy
selected_team_names = st.multiselect(
    "Wybierz drużyny grające tego dnia:",
    options=list(TEAMS_DB.keys()),
    default=list(TEAMS_DB.keys())[:2]
)

# Przycisk startowy
if st.button("🔍 Skanuj zaznaczone drużyny"):
    if not selected_team_names:
        st.warning("Wybierz przynajmniej jedną drużyny z listy.")
    else:
        teams_found = {name: TEAMS_DB[name] for name in selected_team_names}
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
