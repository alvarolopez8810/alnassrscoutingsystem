# -*- coding: utf-8 -*-
"""
saff.py - Scraping functionality for SAFF website

This module provides functions to scrape match data and team information
from the Saudi Arabian Football Federation (SAFF) website.
"""

import requests
from bs4 import BeautifulSoup

# Mapeo de nombres de equipos a sus archivos de logo
# Usamos los nombres exactos que vienen de la web de SAFF
team_logos = {
    # Equipos con sus nombres exactos de la web SAFF
    "Al Ittihad": "alittihad.png",
    "Al Fateh": "alfateh.png",
    "Al Nassr": "alnassr.png",
    "Al Fayha": "alfayha.png",
    "Al Okhdood": "alokhdood.png",
    "Al Hazem": "alhazem.png",
    "Al Jabalin": "aljabalain.png",
    "Al Ettifaq": "alettifaq.png",
    "Al Raed": "alraed.png",
    "NEOM": "neom.png",
    "Al Qadisiyah": "alqadsiah.png",
    "Al Taawoun": "altaawoun.png",
    "Al Wehda": "alwehda.png",
    "Al Najmah": "alnajma.png",
    "Al Hilal": "alhilal.png",
    "Al Shabab": "alshabab.png",
    "Al Ahli": "alahli.png",
    "Al Kholood": "alkholood.png",
    "Al Orobah": "AlOrobah.png",
    "Al Riyadh": "alriyadh.png",
    "Al Khaleej": "alkhaleej.png",
    "Al Bukiryah": "albukiryahfc.png",
    "Damac": "damac.png",
    "Al Adalah": "aladalahclub.png"
}

def get_team_logo(team_name):
    """
    Obtiene el nombre del archivo del logo del equipo.
    
    Args:
        team_name (str): Nombre del equipo
        
    Returns:
        str: Nombre del archivo del logo o None si no se encuentra
    """
    # Primero intentamos con el nombre exacto
    if team_name in team_logos:
        return team_logos[team_name]
    
    # Si no se encuentra, intentamos con una coincidencia parcial
    for name, logo in team_logos.items():
        if team_name.lower() in name.lower() or name.lower() in team_name.lower():
            return logo
    
    # Si no se encuentra ninguna coincidencia
    return None

def scrape_standings(url):
    """
    Scrapea la tabla de posiciones de una liga de fútbol desde la URL.

    Args:
        url (str): La URL de la página con la tabla.

    Returns:
        list: Una lista de diccionarios con la información de cada equipo.
    """
    try:
        # Realizar la petición GET para obtener el contenido de la página
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error si la petición falla

        # Parsear el HTML con Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrar la tabla de posiciones por su encabezado y clase
        standings_table = soup.find('p', string='Standing of Jawwy Elite League U-21').find_next('table')

        # Encontrar el cuerpo de la tabla (tbody) donde están las filas con los datos
        table_body = standings_table.find('tbody')

        if not table_body:
            print("No se encontró el cuerpo de la tabla.")
            return []

        # Crear una lista para almacenar los datos
        standings_data = []

        # Recorrer cada fila (tr) del cuerpo de la tabla
        for row in table_body.find_all('tr'):
            # Encontrar todas las celdas (td) de la fila
            cells = row.find_all('td')

            # Asegurarse de que la fila tenga el número de celdas esperado
            if len(cells) >= 12:  # 12 porque hay celdas que son solo íconos o padding
                # Extraer la información
                rank = cells[1].get_text(strip=True)
                team_name = cells[3].get_text(strip=True)
                played = cells[4].get_text(strip=True)
                won = cells[5].get_text(strip=True)
                drawn = cells[6].get_text(strip=True)
                lost = cells[7].get_text(strip=True)
                goals_for = cells[8].get_text(strip=True)
                goals_against = cells[9].get_text(strip=True)
                goal_difference = cells[10].get_text(strip=True)
                points = cells[11].get_text(strip=True)
                
                # Obtener el logo del equipo
                team_logo = get_team_logo(team_name)

                # Crear un diccionario para el equipo
                team_data = {
                    'rank': rank,
                    'team': team_name,
                    'logo': team_logo,  # Añadimos el logo al diccionario
                    'played': played,
                    'won': won,
                    'drawn': drawn,
                    'lost': lost,
                    'goals_for': goals_for,
                    'goals_against': goals_against,
                    'goal_difference': goal_difference,
                    'points': points
                }

                # Agregar el diccionario a la lista
                standings_data.append(team_data)

        return standings_data

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la URL: {e}")
        return []

def scrape_full_schedule(url):
    """
    Scrapea el calendario de partidos completo de la página de la SAFF,
    manejando las variaciones en la estructura de la tabla de forma más robusta.

    Args:
        url (str): La URL de la página con el calendario.

    Returns:
        list: Una lista de diccionarios con los detalles de cada partido.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontramos la tabla de partidos dentro del contenedor de la vista de escritorio
        schedule_table = soup.find('div', class_='d-none d-lg-block').find('table')
        if not schedule_table:
            print("No se encontró la tabla de partidos en la página.")
            return []

        matches_data = []
        rows = schedule_table.find('tbody').find_all('tr')

        current_date = ""

        for row in rows:
            cells = row.find_all('td', recursive=False)

            # Filtramos filas vacías o de relleno
            if not cells or len(cells) < 2:
                continue

            # Verificamos si la fila es el inicio de un nuevo día (tiene 'rowspan')
            # y tiene un número de celdas para un partido completo
            if 'rowspan' in cells[0].attrs and len(cells) >= 7:
                current_date = cells[0].get_text(strip=True)
                time = cells[1].get_text(strip=True)
                home_team = cells[2].get_text(strip=True)
                score = cells[3].get_text(strip=True)
                away_team = cells[4].get_text(strip=True)
                week = cells[5].get_text(strip=True)
                stadium = cells[6].get_text(strip=True)
            # Para las filas que no tienen la celda de la fecha, pero tienen los demás datos
            elif len(cells) >= 6:
                time = cells[0].get_text(strip=True)
                home_team = cells[1].get_text(strip=True)
                score = cells[2].get_text(strip=True)
                away_team = cells[3].get_text(strip=True)
                week = cells[4].get_text(strip=True)
                stadium = cells[5].get_text(strip=True)
            else:
                continue

            # Obtener logos de los equipos
            home_team_logo = get_team_logo(home_team)
            away_team_logo = get_team_logo(away_team)

            match_data = {
                'date': current_date,
                'time': time,
                'home_team': home_team,
                'home_team_logo': home_team_logo,
                'score': score,
                'away_team': away_team,
                'away_team_logo': away_team_logo,
                'week': week,
                'stadium': stadium
            }
            matches_data.append(match_data)

        return matches_data

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la URL: {e}")
        return []
    except Exception as e:
        print(f"Ocurrió un error inesperado al procesar el HTML: {e}")
        return []

if __name__ == '__main__':
    # Ejemplo de uso para la tabla de posiciones
    print("=== Tabla de Posiciones ===")
    standings_url = 'https://www.saff.com.sa/en/championship.php?id=350'
    standings = scrape_standings(standings_url)
    
    if standings:
        for team in standings:
            print(f"{team['rank']}. {team['team']} - Puntos: {team['points']} (Logo: {team.get('logo', 'No disponible')})")
    
    # Ejemplo de uso para el calendario
    print("\n=== Próximos Partidos ===")
    schedule_url = 'https://www.saff.com.sa/en/championship.php?id=350&type=all'
    schedule = scrape_full_schedule(schedule_url)
    
    if schedule:
        for match in schedule[:5]:  # Mostrar solo los primeros 5 partidos como ejemplo
            print(f"{match['date']} {match['time']}: {match['home_team']} vs {match['away_team']} ({match['score']})")
            print(f"   Logos: {match.get('home_team_logo', '?')} vs {match.get('away_team_logo', '?')}")
            print()
