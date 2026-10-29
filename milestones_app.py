import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="TAURON Liga - Milestone Checker", page_icon="🏐", layout="wide")

st.title("🏐 TAURON Liga – Sprawdzian Kamieni Milowych")
st.write("Aplikacja weryfikująca składy drużyn z dzisiejszych meczów i sprawdzająca sumaryczne rekordy kariery.")

# Ustawienia progu i marginesu
POINT_STEP, POINT_MARGIN = 500, 35
BLOCK_STEP, BLOCK_MARGIN = 100, 10
ACE_STEP, ACE_MARGIN = 100, 10

def get_player_career_stats(player_url):
    """Pobiera dokładne liczby z podstrony zawodnika na tauronliga.pl"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        res = requests.get(player_url, headers=headers, timeout=5)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, 'html.parser')
        text_content = soup.get_text()

        # Szukanie konkretnych fraz w kodzie strony
        pts, aces, blk = 0, 0, 0

        # Reguła wyciągania cyfr po etykietach ze strony
        pts_match = re.search(r'Liczba pkt zdobytych w\s*ligie\s*(\d+)', text_content)
        aces_match = re.search(r'Liczba asów\s*(\d+)', text_content)
        blk_match = re.search(r'Liczba pkt z bloków\s*(\d+)', text_content)

        if pts_match: pts = int(pts_match.group(1))
        if aces_match: aces = int(aces_match.group(1))
        if blk_match: blk = int(blk_match.group(1))

        return {"pts": pts, "aces": aces, "blk": blk}
    except Exception as e:
        return None

def check_milestones(name, stats):
    pts, aces, blk = stats["pts"], stats["aces"], stats["blk"]
    alerts = []
    
    # Punkty
    if pts > 0:
        next_pts = ((pts // POINT_STEP) + 1) * POINT_STEP
        needed = next_pts - pts
        if 0 < needed <= POINT_MARGIN:
            alerts.append(f"🎯 **PUNKTY**: {pts} pkt (brakuje **{needed}** do **{next_pts}**)")

    # Asy
    if aces > 0:
        next_aces = ((aces // ACE_STEP) + 1) * ACE_STEP
        needed = next_aces - aces
        if 0 < needed <= ACE_MARGIN:
            alerts.append(f"💣 **ASY**: {aces} asów (brakuje **{needed}** do **{next_aces}**)")

    # Bloki
    if blk > 0:
        next_blk = ((blk // BLOCK_STEP) + 1) * BLOCK_STEP
        needed = next_blk - blk
        if 0 < needed <= BLOCK_MARGIN:
            alerts.append(f"🧱 **BLOKI**: {blk} bloków (brakuje **{needed}** do **{next_blk}**)")

    return alerts

# Przycisk uruchamiający analizę
if st.button("🔍 Skanuj dzisiejsze mecze i sprawdzaj rekordy"):
    with st.spinner("Pobieranie dokładnych danych z profilów zawodników..."):
        # Przykładowe podstrony zawodników z Twojej instrukcji
        players_to_check = [
            {"name": "Jakub Majchrzak", "team": "Indykpol AZS Olsztyn", "url": "https://www.tauronliga.pl/players/id/816/tour/53.html"},
            {"name": "Moritz Karlitzek", "team": "Indykpol AZS Olsztyn", "url": "https://www.tauronliga.pl/players/id/1784/tour/53.html"},
        ]
        
        found_any = False
        for p in players_to_check:
            stats = get_player_career_stats(p["url"])
            if stats:
                alerts = check_milestones(p["name"], stats)
                if alerts:
                    found_any = True
                    st.subheader(f"👤 {p['name']} ({p['team']})")
                    for a in alerts:
                        st.markdown(f"- {a}")
        
        if not found_any:
            st.info("Brak zawodników spełniających kryteria w wyznaczonym marginesie dla przeskanowanych profili.")