import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="TAURON Liga - Milestone Checker", page_icon="🏐", layout="wide")

st.title("🏐 TAURON Liga – Poprawiony Parser Statystyk")
st.write("Aplikacja korzystająca z parsowania tabel strukturalnych tauronliga.pl.")

POINT_STEP, POINT_MARGIN = 500, 35
BLOCK_STEP, BLOCK_MARGIN = 100, 10
ACE_STEP, ACE_MARGIN = 100, 10

def get_player_career_stats(player_url):
    # Bogatsze nagłówki udające prawdziwą przeglądarkę, aby uniknąć blokady 403
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

        # Szukamy wierszy tabeli lub elementów listy, gdzie statystyki są przechowywane parami
        # Przeszukujemy wszystkie wiersze tabel (tr) lub bloki tekstowe
        rows = soup.find_all(['tr', 'li', 'div'])
        for row in rows:
            text = row.get_text(separator=" ", strip=True)
            
            # Szukamy etykiet i wyciągamy liczby z tego samego lub sąsiadujących elementów
            if "Liczba pkt zdobytych w lidze" in text:
                # Wyciągnij wszystkie cyfry z tego wiersza
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    # Zazwyczaj ostatnia lub odpowiednia liczba w wierszu to szukana wartość
                    pts = int(numbers[-1])
            
            if "Liczba asów" in text:
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    aces = int(numbers[-1])
                    
            if "Liczba pkt z bloków" in text:
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    blk = int(numbers[-1])

        return {"pts": pts, "aces": aces, "blk": blk}
    except Exception as e:
        return {"error": str(e)}

if st.button("🔍 Przetestuj pobieranie danych"):
    test_urls = [
        {"name": "Moritz Karlitzek", "url": "https://www.tauronliga.pl/players/id/1784/tour/53.html"},
        {"name": "Jakub Majchrzak", "url": "https://www.tauronliga.pl/players/id/816/tour/53.html"}
    ]
    
    for p in test_urls:
        st.write(f"### Sprawdzam: {p['name']}")
        result = get_player_career_stats(p["url"])
        
        if "error" in result:
            st.error(f"Nie udało się pobrać: {result['error']}")
        else:
            st.success(f"Odczytano poprawnie! Punkty: **{result['pts']}**, Asy: **{result['aces']}**, Bloki: **{result['blk']}**")
            
            # Sprawdzenie marginesów
            pts, aces, blk = result["pts"], result["aces"], result["blk"]
            if pts > 0:
                next_pts = ((pts // POINT_STEP) + 1) * POINT_STEP
                if 0 < (next_pts - pts) <= POINT_MARGIN:
                    st.info(f"🎯 PUNKTY w strefie marginesu! Brakuje {next_pts - pts} do {next_pts}")
            if aces > 0:
                next_aces = ((aces // ACE_STEP) + 1) * ACE_STEP
                if 0 < (next_aces - aces) <= ACE_MARGIN:
                    st.info(f"💣 ASY w strefie marginesu! Brakuje {next_aces - aces} do {next_aces}")
            if blk > 0:
                next_blk = ((blk // BLOCK_STEP) + 1) * BLOCK_STEP
                if 0 < (next_blk - blk) <= BLOCK_MARGIN:
                    st.info(f"🧱 BLOKI w strefie marginesu! Brakuje {next_blk - blk} do {next_blk}")
        st.divider()
