import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="TAURON Liga - Milestone Checker", page_icon="🏐", layout="wide")

st.title("🏐 TAURON Liga – Skaner na żywo")
st.write("Aplikacja analizuje składy i na bieżąco raportuje postępy.")

POINT_STEP, POINT_MARGIN = 500, 35
BLOCK_STEP, BLOCK_MARGIN = 100, 10
ACE_STEP, ACE_MARGIN = 100, 10

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.tauronliga.pl/'
    }

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

# Przycisk uruchamiający skanowanie z widocznym postępem
if st.button("🚀 Uruchom szybki skan drużyny"):
    
    team_url = "https://www.tauronliga.pl/teams/id/24.html" # Olsztyn
    st.info("Pobieram skład drużyny...")
    
    try:
        res = requests.get(team_url, headers=get_headers(), timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        player_links = []
        seen_urls = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if "/players/id/" in href and "/tour/" in href: # Dokładniejsze dopasowanie profilu
                full_url = href if href.startswith("http") else f"https://www.tauronliga.pl{href}"
                name = a.get_text(strip=True)
                if name and full_url not in seen_urls:
                    seen_urls.add(full_url)
                    player_links.append({"name": name, "url": full_url})
        
        if not player_links:
            # Fallback jeśli selektor nie złapał
            player_links = [
                {"name": "Moritz Karlitzek", "url": "https://www.tauronliga.pl/players/id/1784/tour/53.html"},
                {"name": "Jakub Majchrzak", "url": "https://www.tauronliga.pl/players/id/816/tour/53.html"}
            ]

        st.write(Znaleziono **{len(player_links)}** zawodników do sprawdzenia. Skanuję po kolei:)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        found_any = False
        total = len(player_links)
        
        for i, player in enumerate(player_links):
            status_text.text(f"Sprawdzam ({i+1}/{total}): {player['name']}...")
            stats = get_player_career_stats(player["url"])
            
            if stats:
                alerts = check_milestones(stats["pts"], stats["aces"], stats["blk"])
                if alerts:
                    found_any = True
                    st.success(f"🚨 **{player['name']}**")
                    for alert in alerts:
                        st.markdown(f"    • {alert}")
                        
            progress_bar.progress((i + 1) / total)
            
        status_text.text("Skanowanie zakończone!")
        if not found_any:
            st.warning("Przeskanowano skład – żaden zawodnik nie znajduje się obecnie w strefie marginesu.")
        else:
            st.balloons()
            
    except Exception as e:
        st.error(f"Wystąpił błąd: {e}")
