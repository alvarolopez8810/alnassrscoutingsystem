import requests
import pandas as pd
import json
import time

# --- Módulos de Selenium ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as SeleniumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LEAGUE_ID = "296"

def get_x_mas_token() -> str:
    print("⏳ Obteniendo token 'x-mas' con Selenium...")
    match_url_example = 'https://www.fotmob.com/es/matches/boca-juniors-vs-river-plate/1kl2p4#4393529'
    selenium_options = SeleniumOptions()
    selenium_options.add_argument("--headless=new")
    selenium_options.add_argument("--disable-gpu")
    selenium_options.add_argument("--no-sandbox")
    selenium_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = None
    x_mas_token = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=selenium_options)
        driver.get(match_url_example)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                message = json.loads(entry["message"])["message"]
                if message.get("method") == "Network.requestWillBeSent":
                    headers = message.get("params", {}).get("request", {}).get("headers", {})
                    if "x-mas" in headers:
                        x_mas_token = headers["x-mas"]
                        print("✅ Token 'x-mas' encontrado!")
                        break
            except (KeyError, TypeError, json.JSONDecodeError):
                continue
    finally:
        if driver:
            driver.quit()
    if not x_mas_token:
        raise ValueError("No se pudo obtener el token 'x-mas'.")
    return x_mas_token

def get_league_data(league_id: str, token: str) -> dict:
    url = f"https://www.fotmob.com/api/leagues?id={league_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'X-Mas': token
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("✅ Petición a la API exitosa (con token).")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al hacer la petición a la API: {e}")
        return None

def get_league_table(data: dict) -> pd.DataFrame:
    """
    Función corregida para extraer la tabla de posiciones desde la estructura anidada.
    """
    if not data.get("table") or not isinstance(data["table"], list) or len(data["table"]) == 0:
        return pd.DataFrame()

    # La ruta correcta es: data['table'][0]['data']['tables']
    # Esto es una lista de todos los grupos.
    main_table_container = data["table"][0]
    groups_list = main_table_container.get("data", {}).get("tables")

    if not groups_list:
        return pd.DataFrame()

    all_tables = []
    for group_data in groups_list:
        group_name = group_data.get("leagueName", "Grupo Desconocido")

        # La lista real de equipos está en group_data['table']['all']
        table_list = group_data.get("table", {}).get("all")

        if not table_list:
            continue

        df = pd.DataFrame(table_list)
        df['Grupo'] = group_name

        rename_map = {
            'name': 'Equipo', 'played': 'PJ', 'wins': 'G', 'draws': 'E',
            'losses': 'P', 'goalConDiff': 'DG', 'pts': 'Pts'
        }
        df.rename(columns=rename_map, inplace=True)

        final_columns = ['Equipo', 'Grupo', 'PJ', 'G', 'E', 'P', 'DG', 'Pts']
        existing_cols = [col for col in final_columns if col in df.columns]
        all_tables.append(df[existing_cols])

    if all_tables:
        print("✅ ¡Tabla de posiciones procesada con éxito!")
        return pd.concat(all_tables, ignore_index=True)

    return pd.DataFrame()


def get_matches(data: dict) -> pd.DataFrame:
    if "matches" in data and "allMatches" in data["matches"]:
        matches_data = data["matches"]["allMatches"]
        processed_matches = [
            {'Jornada': match.get('roundName', 'N/A'),
             'Fecha': match['status'].get('startTimeStr', 'N/A'),
             'Equipo Local': match['home']['name'],
             'Equipo Visitante': match['away']['name'],
             'Resultado': f"{match['status'].get('scoreStr', 'vs')}"}
            for match in matches_data
        ]
        return pd.DataFrame(processed_matches)
    return pd.DataFrame()


# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    try:
        api_token = get_x_mas_token()
        league_data = get_league_data(LEAGUE_ID, api_token)

        if league_data:
            with open('datos_liga_crudos.json', 'w', encoding='utf-8') as f:
                json.dump(league_data, f, ensure_ascii=False, indent=4)
            print("\n✅ Datos crudos de la liga guardados en 'datos_liga_crudos.json'")

            print("\n--- 📊 TABLA DE POSICIONES ---")
            table_df = get_league_table(league_data)
            if not table_df.empty:
                print(table_df.to_string())

            print("\n\n--- ⚽ FIXTURE / PARTIDOS ---")
            matches_df = get_matches(league_data)
            if not matches_df.empty:
                print(matches_df.to_string())

    except Exception as e:
        print(f"\nHa ocurrido un error general en la ejecución: {e}")
