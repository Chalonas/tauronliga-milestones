import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="TAURON Liga - Milestone Checker", page_icon="🏐", layout="wide")

st.title("🏐 TAURON Liga – Diagnostyka Statystyk")
st.write("Ta wersja pokazuje odczytane dane dla każdego zawodnika, żeby upewnić się, czy parser działa poprawnie.")

POINT_STEP, POINT_MARGIN = 500, 35
BLOCK_STEP, BLOCK_MARGIN = 100, 10
ACE_STEP, ACE_MARGIN = 100, 10

def get_player_career_stats(player_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        res = requests.get(player_url, headers=headers, timeout=5)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, 'html.parser')
        text_content = soup.get_text()

        pts, aces, blk = 0, 0, 0

        pts_match = re.search(r'Liczba pkt zdobytych w\s*ligie\s*(\d+)', text_content)
        aces_match = re.search(r'Liczba asów\s*(\d+)', text_content)
        blk_match = re.search(r'Liczba pkt z bloków\s*(\d+)', text_content)

        if pts_match: pts = int(pts_match.group(1))
        if aces_match: aces = int(aces_match.group(1))
        if blk_match: blk = int(blk_match.group(1))

        return {"pts": pts, "aces": aces, "blk": blk}
    except Exception as e:
        return None

if st.button("🧪 Uruchom test i pokaż odczytane statystyki"):
    # Kilka przykładowych ID do testu
    test_players = [
        {"name": "Zawodnik Testowy 1", "url": "https://www.tauronliga.pl/players/id/650/tour/53.html"},
        {"name": "Zawodnik Testowy 2", "url": "https://www.tauronliga.pl/players/id/1784/tour/53.html"},
        {"name": "Zawodnik Testowy 3", "url": "https://www.tauronliga.pl/players/id/1020/tour/53.html"}
    ]
    
    for p in test_players:
        stats = get_player_career_stats(p["url"])
        if stats:
            st.write(f"**Profil:** {p['url']}")
            st.write(f"➡️ Odczytano: Punkty = **{stats['pts']}**, Asy = **{stats['aces']}**, Bloki = **{stats['blk']}**")
            
            # Sprawdzenie marginesów
            pts, aces, blk = stats["pts"], stats["aces"], stats["blk"]
            if pts > 0:
                next_pts = ((pts // POINT_STEP) + 1) * POINT_STEP
                if 0 < (next_pts - pts) <= POINT_MARGIN:
                    st.success(f"🎯 Trafienie w punkty! Brakuje {next_pts - pts} do {next_pts}")
            if aces > 0:
                next_aces = ((aces // ACE_STEP) + 1) * ACE_STEP
                if 0 < (next_aces - aces) <= ACE_MARGIN:
                    st.success(f"💣 Trafienie w asy! Brakuje {next_aces - aces} do {next_aces}")
            if blk > 0:
                next_blk = ((blk // BLOCK_STEP) + 1) * BLOCK_STEP
                if 0 < (next_blk - blk) <= BLOCK_MARGIN:
                    st.success(f"🧱 Trafienie w bloki! Brakuje {next_blk - blk} do {next_blk}")
            st.divider()
        else:
            st.error(f"Nie udało się pobrać strony: {p['url']}")
