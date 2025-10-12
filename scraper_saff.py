import requests
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    """Crea una sesión con reintentos automáticos"""
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    return session

def scrape_schedule(league_id):
    """
    Scrapea el calendario de una liga específica de SAFF.
    
    Args:
        league_id (int): ID de la liga SAFF (ej: 350 para U21)
    
    Returns:
        list: Lista de diccionarios con información de cada partido
    """
    url = f'https://www.saff.com.sa/en/championship.php?id={league_id}&type=all'
    
    try:
        session = create_session()
        response = session.get(url, timeout=20)
        response.raise_for_status()
        time.sleep(1)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        schedule_table = soup.find('div', class_='d-none d-lg-block')
        if schedule_table:
            schedule_table = schedule_table.find('table')
        else:
            schedule_table = soup.find('table')
        
        if not schedule_table:
            return []

        table_body = schedule_table.find('tbody')
        if not table_body:
            rows = schedule_table.find_all('tr')
        else:
            rows = table_body.find_all('tr')

        matches_data = []
        current_date = ""

        for row in rows:
            cells = row.find_all('td', recursive=False)
            if not cells or len(cells) < 2:
                continue

            try:
                if cells[0].has_attr('rowspan'):
                    current_date = cells[0].get_text(strip=True)
                    if len(cells) >= 7:
                        time_match = cells[1].get_text(strip=True)
                        home_team = cells[2].get_text(strip=True)
                        score = cells[3].get_text(strip=True)
                        away_team = cells[4].get_text(strip=True)
                        week = cells[5].get_text(strip=True)
                        stadium = cells[6].get_text(strip=True)
                    else:
                        continue
                elif len(cells) >= 6:
                    time_match = cells[0].get_text(strip=True)
                    home_team = cells[1].get_text(strip=True)
                    score = cells[2].get_text(strip=True)
                    away_team = cells[3].get_text(strip=True)
                    week = cells[4].get_text(strip=True)
                    stadium = cells[5].get_text(strip=True)
                else:
                    continue

                match_data = {
                    'date': current_date,
                    'time': time_match,
                    'home_team': home_team,
                    'score': score,
                    'away_team': away_team,
                    'week': week,
                    'stadium': stadium,
                    'fixture': f"{home_team} vs {away_team}"
                }
                
                matches_data.append(match_data)
                
            except Exception:
                continue

        return matches_data

    except Exception as e:
        print(f"Error scraping league {league_id}: {e}")
        return []
