import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="TAURON Liga - Milestone Checker", page_icon="🏐", layout="wide")

st.title("🏐 TAURON Liga – Precyzyjny Skaner Statystyk")
st.write("Wersja oparta na analizie struktury tabelarycznej stron zawodników.")

POINT_STEP, POINT_MARGIN = 500, 35
BLOCK_STEP, BLOCK_MARGIN = 100, 10
ACE_STEP, ACE_MARGIN = 100, 10

def get_player_career_stats(player_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.tauronliga.pl/'
    }
    try:
        res = requests.get(player_url, headers=headers, timeout=10)
        if res.status_code != 200:
            return {"error": f"Błąd HTTP: {res.status_code}"}
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        pts, aces, blk = 0, 0, 0

        # Przeszukujemy wiersze tabel profilu zawodnika
        for tr in soup.find_all('tr'):
            tds = tr.find_all(['td', 'th'])
            if len(tds) >= 2:
                label = tds[0].get_text(strip=True).lower()
                value_text = tds[1].get_text(strip=True)
                
                # Wyciągamy pierwszą napotkaną liczbę z kolumny wartości
                match = re.search(r'\d+', value_text)
                if match:
                    val = int(match.group())
                    
                    if "liczba pkt zdobytych w lidze" in label or ("liczba" in label and "pkt" in label and "lidze" in label):
                        pts = val
                    elif "liczba asów" in label:
                        aces = val
                    elif "liczba pkt z bloków" in label or "blok" in label:
                        blk = val

        return {"pts": pts, "aces": aces, "blk": blk}
    except Exception as e:
        return {"error": str(e)}

if st.button("🚀 Uruchom precyzyjny skan zawodników"):
    test_urls = [
        {"name": "Moritz Karlitzek", "url": "https://www.tauronliga.pl/players/id/1784/tour/53.html"},
        {"name": "Jakub Majchrzak", "url": "https://www.tauronliga.pl/players/id/816/tour/53.html"}
    ]
    
    for p in test_urls:
        st.write(f"### Zawodnik: {p['name']}")
        result = get_player_career_stats(p["url"])
        
        if "error" in result:
            st.error(f"Nie udało się pobrać: {result['error']}")
        else:
            st.success(f"📊 Odczytane statystyki kariery: Punkty = **{result['pts']}**, Asy = **{result['aces']}**, Bloki = **{result['blk']}**")
            
            # Weryfikacja progów i marginesów
            pts, aces, blk = result["pts"], result["aces"], result["blk"]
            
            # Punkty
            if pts > 0:
                next_pts = ((pts // POINT_STEP) + 1) * POINT_STEP
                needed_pts = next_pts - pts
                if 0 < needed_pts <= POINT_MARGIN:
                    st.info(f"🎯 **PUNKTY**: {pts} pkt -> Brakuje **{needed_pts}** do progu {next_pts}!")
            
            # Asy
            if aces > 0:
                next_aces = ((aces // ACE_STEP) + 1) * ACE_STEP
                needed_aces = next_aces - aces
                if 0 < needed_aces <= ACE_MARGIN:
                    st.info(f"💣 **ASY**: {aces} asów -> Brakuje **{needed_aces}** do progu {next_aces}!")
            
            # Bloki
            if blk > 0:
                next_blk = ((blk // BLOCK_STEP) + 1) * BLOCK_STEP
                needed_blk = next_blk - blk
                if 0 < needed_blk <= BLOCK_MARGIN:
                    st.info(f"🧱 **BLOKI**: {blk} bloków -> Brakuje **{needed_blk}** do progu {next_blk}!")
        st.divider()
