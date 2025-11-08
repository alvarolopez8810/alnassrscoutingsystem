"""
OBISEN ScoutIA - Sistema de Análisis de Scouting

SYSTEM PROMPT / FILOSOFÍA DE RESPUESTAS:
Eres un asistente especializado en análisis de datos deportivos integrado en una aplicación Streamlit.

INSTRUCCIONES CRÍTICAS:
1. SIEMPRE proporciona información específica y detallada:
   - Usa NOMBRES COMPLETOS de jugadores, equipos, etc.
   - Proporciona NÚMEROS y ESTADÍSTICAS exactas
   - NO uses frases vagas como "encontré varios..." o "principalmente..."

2. Cuando analices un Report o documento:
   - Lee TODO el contenido cuidadosamente
   - Extrae información específica (nombres, números, fechas)
   - Cita datos exactos del documento

3. Formato de respuestas:
   - Para listas de jugadores: "Los jugadores son: [Nombre1], [Nombre2], [Nombre3]"
   - Para estadísticas: Proporciona valores numéricos exactos
   - Para comparaciones: Usa tablas o listas ordenadas

4. NUNCA respondas con:
   ❌ "Encontré X jugadores principalmente..."
   ❌ "Hay varios jugadores..."
   ❌ "Algunos resultados incluyen..."
   
   ✅ EN SU LUGAR: "Los 5 jugadores son: Lionel Messi, Cristiano Ronaldo..."

5. Si tienes acceso a datos estructurados o documentos:
   - Procesa TODO el contenido disponible
   - Extrae TODOS los nombres y datos relevantes
   - Presenta la información completa
"""

import streamlit as st
import pandas as pd
import base64
import io
from datetime import datetime, date
import time
import fcntl
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
# from generate_individual_pdf import generate_individual_report_pdf

# File locking utilities for concurrent access
def safe_read_excel(file_path, max_retries=5, retry_delay=0.5):
    """Safely read Excel file with retry logic"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                df = pd.read_excel(file_path)
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                raise Exception(f"Failed to read {file_path} after {max_retries} attempts: {e}")
    return pd.DataFrame()

def safe_write_excel(df, file_path, max_retries=5, retry_delay=0.5):
    """Safely write Excel file with file locking and retry logic"""
    for attempt in range(max_retries):
        lock_file = f"{file_path}.lock"
        lock_fd = None
        try:
            # Create lock file
            lock_fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            
            # Write to a temporary file first
            temp_file = f"{file_path}.tmp"
            df.to_excel(temp_file, index=False)
            
            # Atomic rename (replaces original file)
            os.replace(temp_file, file_path)
            
            # Release lock
            os.close(lock_fd)
            os.remove(lock_file)
            return True
            
        except FileExistsError:
            # Lock file exists, another process is writing
            if lock_fd is not None:
                os.close(lock_fd)
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                raise Exception(f"Could not acquire lock for {file_path} after {max_retries} attempts")
        except Exception as e:
            # Clean up on error
            if lock_fd is not None:
                try:
                    os.close(lock_fd)
                    if os.path.exists(lock_file):
                        os.remove(lock_file)
                except:
                    pass
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
            else:
                raise Exception(f"Failed to write {file_path} after {max_retries} attempts: {e}")
    return False

# Google Sheets Integration
@st.cache_resource
def get_google_sheets_client():
    """Initialize Google Sheets client with credentials from Streamlit secrets or Render environment variables"""
    try:
        credentials_dict = None
        
        # Try to load from local credentials.json file FIRST (for local development)
        if os.path.exists('credentials.json'):
            try:
                with open('credentials.json', 'r') as f:
                    credentials_dict = json.load(f)
                print("✅ Credentials loaded from credentials.json")
            except Exception as e:
                print(f"❌ Error loading credentials.json: {e}")
        
        # Try to load from Render environment variable (GOOGLE_CREDENTIALS)
        if credentials_dict is None and os.getenv('GOOGLE_CREDENTIALS'):
            try:
                credentials_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
                print("✅ Credentials loaded from GOOGLE_CREDENTIALS environment variable")
            except Exception as e:
                print(f"❌ Error loading from GOOGLE_CREDENTIALS: {e}")
        
        # Try to get credentials from Streamlit secrets (for Streamlit Cloud)
        if credentials_dict is None:
            try:
                if 'gcp_service_account' in st.secrets:
                    credentials_dict = dict(st.secrets['gcp_service_account'])
                    print("✅ Credentials loaded from Streamlit secrets")
            except:
                pass
        
        # If we have credentials, authorize
        if credentials_dict:
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
            client = gspread.authorize(credentials)
            print("✅ Google Sheets client authorized successfully")
            return client
        else:
            print("❌ No credentials found in any location")
            return None
            
    except Exception as e:
        print(f"❌ Error in get_google_sheets_client: {e}")
        import traceback
        traceback.print_exc()
        return None

@st.cache_data(ttl=60)  # Cache for 60 seconds to avoid API quota limits
def read_google_sheet(sheet_name, worksheet_name='Sheet1'):
    """Read data from Google Sheet and return as DataFrame"""
    try:
        client = get_google_sheets_client()
        if client is None:
            # Fallback to local Excel
            return safe_read_excel(f'{sheet_name}.xlsx')
        
        sheet = client.open(sheet_name)
        worksheet = sheet.worksheet(worksheet_name)
        data = worksheet.get_all_records()
        
        # Check if data is valid
        if not data or not isinstance(data, list):
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        # If quota exceeded, try to return cached data or empty DataFrame
        if "Quota exceeded" in str(e):
            st.warning(f"⚠️ Google Sheets API limit reached. Please wait a moment and try again.")
            return pd.DataFrame()
        
        # Don't show error for connection issues or common errors
        error_str = str(e).lower()
        should_show_error = (
            "Response [200]" not in error_str and 
            "individual_reports" not in sheet_name and
            "connection" not in error_str and  # Silenciar errores de conexión
            "reset by peer" not in error_str and  # Silenciar connection reset
            "aborted" not in error_str  # Silenciar connection aborted
        )
        
        if should_show_error:
            st.error(f"Error reading Google Sheet '{sheet_name}': {e}")
        
        # Return empty DataFrame to trigger fallback
        return pd.DataFrame()

def write_google_sheet(df, sheet_name, worksheet_name='Sheet1'):
    """Write DataFrame to Google Sheet"""
    try:
        client = get_google_sheets_client()
        if client is None:
            print("❌ Google Sheets client is None - no credentials found")
            return False
        
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # Convert datetime/timestamp columns to strings
        for col in df_clean.columns:
            if pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].astype(str)
        
        # Replace NaN values with empty strings to avoid JSON errors
        df_clean = df_clean.fillna('')
        
        # Convert all data to strings to ensure JSON compatibility
        df_clean = df_clean.astype(str)
        
        # Open or create the sheet
        try:
            sheet = client.open(sheet_name)
            print(f"✅ Opened Google Sheet: {sheet_name}")
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"⚠️ Sheet '{sheet_name}' not found, creating new one...")
            sheet = client.create(sheet_name)
            # Share with everyone (or specific emails)
            sheet.share('', perm_type='anyone', role='writer')
        
        # Get or create worksheet
        try:
            worksheet = sheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
        
        # Clear existing data
        worksheet.clear()
        
        # Write headers and data
        data_to_write = [df_clean.columns.values.tolist()] + df_clean.values.tolist()
        worksheet.update(data_to_write)
        
        print(f"✅ Successfully wrote {len(df)} rows to {sheet_name}")
        return True
    except Exception as e:
        print(f"❌ Error in write_google_sheet: {e}")
        import traceback
        traceback.print_exc()
        return False

def append_to_google_sheet(df_new, sheet_name, worksheet_name='Sheet1'):
    """Append new data to existing Google Sheet"""
    try:
        print(f"📝 Attempting to append {len(df_new)} rows to {sheet_name}...")
        
        # Read existing data
        df_existing = read_google_sheet(sheet_name, worksheet_name)
        
        # Combine with new data
        if not df_existing.empty:
            print(f"📊 Found {len(df_existing)} existing rows, combining...")
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            print("📊 No existing data, creating new sheet...")
            df_combined = df_new
        
        # Write back
        result = write_google_sheet(df_combined, sheet_name, worksheet_name)
        
        if result:
            print(f"✅ Successfully appended data to {sheet_name}")
        else:
            print(f"❌ Failed to append data to {sheet_name}")
        
        return result
    except Exception as e:
        print(f"❌ Error in append_to_google_sheet: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_player_photo(player_name):
    """Find player photo with different extensions and name formats"""
    import unicodedata
    
    # Remove accents from name
    def remove_accents(text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
    # Try different name formats (prioritize underscore format used in Google Sheets)
    name_formats = [
        player_name.replace(' ', '_'),              # Obed_Vargas (PRIORITY - matches Google Sheets)
        player_name.replace(' ', ''),               # ObedVargas (fallback)
        remove_accents(player_name).replace(' ', '_'),  # Obed_Vargas (without accents)
        remove_accents(player_name).replace(' ', ''),   # ObedVargas (without accents)
        player_name,                                 # Obed Vargas (fallback)
    ]
    
    # Try different extensions (prioritize .jpg as it's the default save format)
    extensions = ['.jpg', '.png', '.jpeg', '.JPG', '.PNG', '.JPEG']
    
    for name_format in name_formats:
        for ext in extensions:
            photo_path = f"player_photos/{name_format}{ext}"
            if os.path.exists(photo_path):
                return photo_path
    
    # If not found, return None
    return None

def find_player_photo_github(player_name):
    """Try to find player photo on GitHub with different name formats"""
    import unicodedata
    
    # Remove accents from name
    def remove_accents(text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
    github_base = "https://raw.githubusercontent.com/alvarolopez8810/alnassrscoutingsystem/main/player_photos/"
    
    # Try different name formats
    name_formats = [
        player_name.replace(' ', '_'),              # Jordan_García
        player_name.replace(' ', ''),               # JordanGarcía
        remove_accents(player_name).replace(' ', '_'),  # Jordan_Garcia
        remove_accents(player_name).replace(' ', ''),   # JordanGarcia
    ]
    
    # Try different extensions
    extensions = ['.jpg', '.png', '.jpeg', '.JPG', '.PNG', '.JPEG']
    
    # Return list of possible URLs to try
    possible_urls = []
    for name_format in name_formats:
        for ext in extensions:
            possible_urls.append(github_base + name_format + ext)
    
    return possible_urls

# Page configuration
try:
    from PIL import Image
    page_icon_img = Image.open('fwcu17.webp')
    st.set_page_config(
        page_title="FIFA U17 World Cup - Scouting Dashboard",
        page_icon=page_icon_img,
        layout="wide",
        initial_sidebar_state="expanded"
    )
except:
    st.set_page_config(
        page_title="FIFA U17 World Cup - Scouting Dashboard",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def main():
    # Initialize authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_photo' not in st.session_state:
        st.session_state.user_photo = None
    
    # Initialize language
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    # Initialize page
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Check authentication
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Apply styling
    apply_custom_css()
    
    # Language toggle button in sidebar
    with st.sidebar:
        # User info at top
        if st.session_state.user_name:
            try:
                from PIL import Image
                import io
                import base64
                
                user_img = Image.open(st.session_state.user_photo)
                user_img.thumbnail((60, 60))
                buffered = io.BytesIO()
                if user_img.mode in ('RGBA', 'LA', 'P'):
                    user_img.save(buffered, format="PNG")
                else:
                    user_img = user_img.convert('RGB')
                    user_img.save(buffered, format="PNG")
                user_img_str = base64.b64encode(buffered.getvalue()).decode()
                user_photo_html = f'<img src="data:image/png;base64,{user_img_str}" style="width: 50px; height: 50px; border-radius: 50%; border: 3px solid #FFC60A; object-fit: cover;">'
            except:
                user_photo_html = '👤'
            
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1a2332 0%, #2d3e50 100%);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 20px;
                    border: 2px solid #FFC60A;
                ">
                    {user_photo_html}
                    <p style="color: white; margin: 10px 0 0 0; font-weight: 600; font-size: 14px;">{st.session_state.user_name}</p>
                    <p style="color: #FFC60A; margin: 3px 0 0 0; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">SCOUT</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### Settings / الإعدادات")
        if st.button("🇸🇦 عربي" if st.session_state.language == 'en' else "🇬🇧 English",
                    key="lang_toggle",
                    help="Toggle Language",
                    use_container_width=True):
            toggle_language()
        
        st.markdown("---")
        
        # Navigation
        if st.session_state.page != 'home':
            if st.button("🏠 " + ("Home" if st.session_state.language == 'en' else "الرئيسية"), 
                        key="btn_home",
                        use_container_width=True):
                st.session_state.page = 'home'
                st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Cerrar Sesión", key="btn_logout", use_container_width=True, type="secondary"):
            logout()
    
    # Show FIFA U17 view directly
    show_fifa_u17_view()


def show_fifa_u17_view():
    """Show FIFA U17 World Cup section with 5 tabs"""
    
    # Country flags emoji mapping - FIFA U17 World Cup 2025 (48 teams)
    COUNTRY_FLAG_EMOJI = {
        'Alemania': '🇩🇪',
        'Germany': '🇩🇪',
        'Arabia Saudita': '🇸🇦',
        'Saudi Arabia': '🇸🇦',
        'Argentina': '🇦🇷',
        'Austria': '🇦🇹',
        'Bélgica': '🇧🇪',
        'Belgium': '🇧🇪',
        'Bolivia': '🇧🇴',
        'Brasil': '🇧🇷',
        'Brazil': '🇧🇷',
        'Burkina Faso': '🇧🇫',
        'Canadá': '🇨🇦',
        'Canada': '🇨🇦',
        'Catar': '🇶🇦',
        'Qatar': '🇶🇦',
        'Chile': '🇨🇱',
        'Colombia': '🇨🇴',
        'Corea del Norte': '🇰🇵',
        'Korea DPR': '🇰🇵',
        'Corea del Sur': '🇰🇷',
        'Korea Republic': '🇰🇷',
        'South Korea': '🇰🇷',
        'Costa de Marfil': '🇨🇮',
        "Côte D'Ivoire": '🇨🇮',
        'Ivory Coast': '🇨🇮',
        'Costa Rica': '🇨🇷',
        'Croacia': '🇭🇷',
        'Croatia': '🇭🇷',
        'Egipto': '🇪🇬',
        'Egypt': '🇪🇬',
        'El Salvador': '🇸🇻',
        'Emiratos Árabes Unidos': '🇦🇪',
        'United Arab Emirates': '🇦🇪',
        'Estados Unidos': '🇺🇸',
        'USA': '🇺🇸',
        'United States': '🇺🇸',
        'Fiyi': '🇫🇯',
        'Fiji': '🇫🇯',
        'Francia': '🇫🇷',
        'France': '🇫🇷',
        'Haití': '🇭🇹',
        'Haiti': '🇭🇹',
        'Honduras': '🇭🇳',
        'Indonesia': '🇮🇩',
        'Inglaterra': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'Irlanda': '🇮🇪',
        'Republic Of Ireland': '🇮🇪',
        'Ireland': '🇮🇪',
        'Italia': '🇮🇹',
        'Italy': '🇮🇹',
        'Japón': '🇯🇵',
        'Japan': '🇯🇵',
        'Malí': '🇲🇱',
        'Mali': '🇲🇱',
        'Marruecos': '🇲🇦',
        'Morocco': '🇲🇦',
        'México': '🇲🇽',
        'Mexico': '🇲🇽',
        'Nueva Caledonia': '🇳🇨',
        'New Caledonia': '🇳🇨',
        'Nueva Zelanda': '🇳🇿',
        'New Zealand': '🇳🇿',
        'Panamá': '🇵🇦',
        'Panama': '🇵🇦',
        'Paraguay': '🇵🇾',
        'Portugal': '🇵🇹',
        'República Checa': '🇨🇿',
        'Czechia': '🇨🇿',
        'Czech Republic': '🇨🇿',
        'Senegal': '🇸🇳',
        'Sudáfrica': '🇿🇦',
        'South Africa': '🇿🇦',
        'Suiza': '🇨🇭',
        'Switzerland': '🇨🇭',
        'Tayikistán': '🇹🇯',
        'Tajikistan': '🇹🇯',
        'Túnez': '🇹🇳',
        'Tunisia': '🇹🇳',
        'Uganda': '🇺🇬',
        'Uzbekistán': '🇺🇿',
        'Uzbekistan': '🇺🇿',
        'Venezuela': '🇻🇪',
        'Zambia': '🇿🇲',
    }
    
    # Keep old COUNTRY_FLAGS for backwards compatibility
    COUNTRY_FLAGS = {
        'Arabia Saudita': 'saff.png',
        'Argentina': 'afa.png',
        'Australia': 'australia.png',
        'Brasil': 'brasil.png',
        'Chile': 'chile.png',
        'Colombia': 'colombiau20.png',
        'Corea del Sur': 'korea.png',
        'Cuba': 'cuba.png',
        'Egipto': 'egipto.webp',
        'España': 'spain.png',
        'Estados Unidos': 'usa.png',
        'Francia': 'francia.png',
        'Italia': 'italia.png',
        'Japón': 'japan.png',
        'Marruecos': 'marruecos.png',
        'México': 'mexico.png',
        'Nigeria': 'nigeria.png',
        'Noruega': 'noruega.png',
        'Nueva Caledonia': 'nuevacaledonia.png',
        'Nueva Zelanda': 'nuevazelanda.png',
        'Panamá': 'panama.png',
        'Paraguay': 'paraguay.webp',
        'Sudáfrica': 'sudafrica.png',
        'Ucrania': 'ucrania.png'
    }
    
    # Back button and Header
    col_back, col_title = st.columns([1, 5])
    
    with col_back:
        if st.button("⬅️ Back" if st.session_state.language == 'en' else "⬅️ رجوع", 
                    key="btn_back_to_home_fifa",
                    help="Return to home" if st.session_state.language == 'en' else "العودة إلى الرئيسية"):
            st.session_state.page = 'home'
            st.rerun()
    
    with col_title:
        # Load FIFA U17 icon
        try:
            from PIL import Image
            import io
            
            icon_img = Image.open('fwcu17.webp')
            icon_img.thumbnail((40, 40))  # Resize icon
            buffered = io.BytesIO()
            
            # Convert to PNG for better compatibility
            if icon_img.mode in ('RGBA', 'LA', 'P'):
                icon_img.save(buffered, format="PNG")
            else:
                icon_img = icon_img.convert('RGB')
                icon_img.save(buffered, format="PNG")
            
            icon_str = base64.b64encode(buffered.getvalue()).decode()
            icon_html = f'<img src="data:image/png;base64,{icon_str}" style="height:35px; vertical-align:middle; margin-right:10px;">'
        except Exception as e:
            print(f"Error loading FIFA U17 icon: {e}")
            icon_html = '⚽ '  # Fallback to emoji if image fails
        
        if st.session_state.language == 'en':
            st.markdown(f"<h2 style='color: #002B5B;'>{icon_html}FIFA WORLD CUP U17</h2>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h2 style='color: #002B5B;'>{icon_html}كأس العالم تحت 17</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create 5 tabs
    if st.session_state.language == 'en':
        tabs = st.tabs([
            "📝 CREATE MATCH REPORT",
            "👤 CREATE INDIVIDUAL REPORT",
            "📈 VIEW MATCH REPORTS",
            "📊 VIEW INDIVIDUAL REPORTS",
            "🗂️ DATABASE"
        ])
    else:
        tabs = st.tabs([
            "📝 إنشاء تقرير مباراة",
            "👤 إنشاء تقرير فردي",
            "📈 تقارير المباريات",
            "📊 تقارير فردية",
            "🗂️ قاعدة بيانات اللاعبين"
        ])
    
    # Tab 0: CREATE MATCH REPORT
    with tabs[0]:
        # Al Nassr Custom CSS for Form
        st.markdown("""
            <style>
            /* Al Nassr Form Styling */
            .stTextInput > div > div > input,
            .stDateInput > div > div > input,
            .stSelectbox > div > div > select {
                background-color: #f5f5f5 !important;
                border: 2px solid #e0e0e0 !important;
                border-radius: 6px !important;
                transition: all 0.3s ease !important;
            }
            
            .stTextInput > div > div > input:focus,
            .stDateInput > div > div > input:focus,
            .stSelectbox > div > div > select:focus {
                border-color: #FFC60A !important;
                box-shadow: 0 0 0 3px rgba(255,198,10,0.1) !important;
            }
            
            .alnassr-header {
                background: #1a2332;
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                margin: 20px 0 15px 0;
                font-size: 16px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .alnassr-title {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 30px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Load Al Nassr Logo
        try:
            from PIL import Image
            import io
            logo_img = Image.open('alnassr.png')
            logo_img.thumbnail((50, 50))
            buffered = io.BytesIO()
            if logo_img.mode in ('RGBA', 'LA', 'P'):
                logo_img.save(buffered, format="PNG")
            else:
                logo_img = logo_img.convert('RGB')
                logo_img.save(buffered, format="PNG")
            logo_str = base64.b64encode(buffered.getvalue()).decode()
            logo_html = f'<img src="data:image/png;base64,{logo_str}" style="height:50px; vertical-align:middle;">'
        except:
            logo_html = '🦅'
        
        # Page Title with Logo
        st.markdown(f"""
            <div class="alnassr-title">
                {logo_html}
                <div>
                    <h2 style="margin:0; color:#1a2332;">{"Create Match Report" if st.session_state.language == 'en' else "إنشاء تقرير مباراة"}</h2>
                    <p style="margin:0; color:#666; font-size:14px;">FIFA U17 World Cup</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Load teams dynamically from WorldCupU17Data (Team column for national teams)
        try:
            df_teams = read_google_sheet('WorldCupU17Data', 'Sheet1')
            # Fallback to local Excel if Google Sheets fails
            if df_teams is None or df_teams.empty:
                try:
                    df_teams = pd.read_excel('dbworldcup17.xlsx')
                except:
                    df_teams = pd.DataFrame()
            
            if not df_teams.empty and 'Team' in df_teams.columns:
                TEAMS_U17 = sorted(df_teams['Team'].dropna().unique().tolist())
            else:
                TEAMS_U17 = []
        except:
            TEAMS_U17 = []
        
        # Match Information Section - Navy Header
        st.markdown("""
            <div class="alnassr-header">
                ℹ️ Match Information
            </div>
        """ if st.session_state.language == 'en' else """
            <div class="alnassr-header">
                ℹ️ معلومات المباراة
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            match_date = st.date_input(
                "Match Date" if st.session_state.language == 'en' else "تاريخ المباراة",
                value=date.today(),
                key="fifa_match_date"
            )
        
        with col2:
            scout_name = st.selectbox(
                "Scout Name" if st.session_state.language == 'en' else "اسم الكشاف",
                options=["Juan Gambero", "Alvaro Lopez", "Rafa Gil"],
                key="fifa_scout_name"
            )
        
        with col3:
            match_phase = st.selectbox(
                "Phase/Round" if st.session_state.language == 'en' else "الجولة/المرحلة",
                ["", "Group Stage", "Round of 16", "Quarter Finals", "Semi Finals", "Final"],
                key="fifa_match_phase"
            )
        
        # Team Selection Section - Navy Header
        st.markdown("""
            <div class="alnassr-header">
                ⚽ Team Selection
            </div>
        """ if st.session_state.language == 'en' else """
            <div class="alnassr-header">
                ⚽ اختيار الفرق
            </div>
        """, unsafe_allow_html=True)
        
        col_home, col_away = st.columns(2)
        
        with col_home:
            home_team = st.selectbox(
                "🏠 Home Team" if st.session_state.language == 'en' else "🏠 الفريق المحلي",
                [""] + TEAMS_U17,
                key="fifa_home_team"
            )
        
        with col_away:
            away_team = st.selectbox(
                "✈️ Away Team" if st.session_state.language == 'en' else "✈️ الفريق الزائر",
                [""] + TEAMS_U17,
                key="fifa_away_team"
            )
        
        # Info message if teams not selected
        if not home_team or not away_team:
            st.markdown("""
                <div style="background: #f0f7ff; border-left: 4px solid #FFC60A; padding: 15px; border-radius: 6px; margin-top: 15px;">
                    <p style="margin: 0; color: #1a2332; font-size: 14px;">
                        <strong>ℹ️ Info:</strong> Please select both home and away teams to configure lineups
                    </p>
                </div>
            """ if st.session_state.language == 'en' else """
                <div style="background: #f0f7ff; border-left: 4px solid #FFC60A; padding: 15px; border-radius: 6px; margin-top: 15px;">
                    <p style="margin: 0; color: #1a2332; font-size: 14px;">
                        <strong>ℹ️ معلومة:</strong> يرجى اختيار الفريق المحلي والزائر لإعداد التشكيلات
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        # Load player data if both teams are selected
        if home_team and away_team:
            try:
                df_players = read_google_sheet('WorldCupU17Data', 'Sheet1')
                # Fallback to local Excel if Google Sheets fails
                if df_players is None or df_players.empty:
                    df_players = pd.read_excel('dbworldcup17.xlsx')
                
                # Use correct column names from WorldCupU17Data Google Sheet
                # Columns: # POS PLAYER NAME ... Team CLUB Nationality
                team_col_match = 'Team'
                position_col_match = 'POS'
                name_col_match = 'PLAYER NAME'
                
                # Verify columns exist
                if not df_players.empty:
                    if 'Team' not in df_players.columns:
                        for col in df_players.columns:
                            if col.lower() in ['team', 'equipo', 'selección']:
                                team_col_match = col
                                break
                    
                    if 'POS' not in df_players.columns:
                        for col in df_players.columns:
                            if 'pos' in col.lower() or 'position' in col.lower():
                                position_col_match = col
                                break
                    
                    if 'PLAYER NAME' not in df_players.columns:
                        for col in df_players.columns:
                            if 'player' in col.lower() or 'name' in col.lower() or 'nombre' in col.lower():
                                name_col_match = col
                                break
                
                # Position order for sorting
                POSITION_ORDER = {'GK': 1, 'RB': 2, 'CB': 3, 'LB': 4, 'DM': 5, 'CM': 6, 'CAM': 7, 'RW': 8, 'LW': 9, 'ST': 10}
                
                # Get players for home team sorted by position (filter by Team)
                home_team_df = df_players[df_players[team_col_match] == home_team].copy()
                home_team_df['pos_order'] = home_team_df[position_col_match].map(POSITION_ORDER).fillna(99)
                home_team_df = home_team_df.sort_values('pos_order')
                home_players = home_team_df[name_col_match].tolist()
                
                # Get players for away team sorted by position (filter by Team)
                away_team_df = df_players[df_players[team_col_match] == away_team].copy()
                away_team_df['pos_order'] = away_team_df[position_col_match].map(POSITION_ORDER).fillna(99)
                away_team_df = away_team_df.sort_values('pos_order')
                away_players = away_team_df[name_col_match].tolist()
                
                # Create player-to-position mapping
                home_player_positions = dict(zip(home_team_df[name_col_match], home_team_df[position_col_match]))
                away_player_positions = dict(zip(away_team_df[name_col_match], away_team_df[position_col_match]))
                
                st.markdown("---")
                
                # Initialize session state for players if not exists
                if 'home_match_players' not in st.session_state:
                    st.session_state.home_match_players = []
                if 'away_match_players' not in st.session_state:
                    st.session_state.away_match_players = []
                
                # Players Section
                col_lineup_home, col_lineup_away = st.columns(2)
                
                # HOME TEAM PLAYERS
                with col_lineup_home:
                    # Get home team flag emoji
                    home_flag_emoji = COUNTRY_FLAG_EMOJI.get(home_team, '🏠')
                    
                    st.markdown(f"### {home_flag_emoji} {home_team}")
                    
                    # Button to add player
                    if st.button("➕ Add Player" if st.session_state.language == 'en' else "➕ إضافة لاعب", key="add_home_player"):
                        st.session_state.home_match_players.append({
                            'id': len(st.session_state.home_match_players),
                            'name': '',
                            'number': 1,
                            'position': '',
                            'starter': 'Sí',
                            'minutes': 90,
                            'performance': 1,
                            'report': ''
                        })
                        st.rerun()
                    
                    st.markdown("---")
                    
                    # Display added players
                    for idx, player_data in enumerate(st.session_state.home_match_players):
                        # Get current name for display
                        current_name = player_data.get('name', 'Not selected')
                        display_name = current_name if current_name else 'Not selected'
                        
                        with st.expander(f"👤 Player {idx+1}: {display_name}", expanded=True):
                            col1, col2, col3 = st.columns([3, 1, 2])
                            
                            with col1:
                                selected_player = st.selectbox(
                                    "Player Name",
                                    [""] + home_players,
                                    index=0 if not player_data['name'] else (home_players.index(player_data['name']) + 1 if player_data['name'] in home_players else 0),
                                    key=f"home_p_name_{idx}"
                                )
                                # Update name if changed
                                current_name = player_data.get('name', '')
                                if selected_player != current_name:
                                    st.session_state.home_match_players[idx]['name'] = selected_player
                                
                                # Auto-completar datos del jugador cuando se selecciona (siempre que haya jugador)
                                if selected_player and selected_player != current_name:
                                    # 1. Buscar número anterior en reportes previos
                                    try:
                                        prev_reports = read_google_sheet('fifa_u17_match_reports', 'Sheet1')
                                        player_prev_reports = prev_reports[prev_reports['Player Name'] == selected_player]
                                        if not player_prev_reports.empty:
                                            # Obtener el número más reciente
                                            last_number = player_prev_reports.iloc[-1]['Number']
                                            if pd.notna(last_number):
                                                st.session_state.home_match_players[idx]['number'] = int(last_number)
                                    except:
                                        pass
                                    
                                    # 2. Buscar año de nacimiento, posición y número en la base de datos
                                    try:
                                        print(f"🔍 Buscando datos para jugador: {selected_player}")
                                        df_players_db = read_google_sheet('WorldCupU17Data', 'Sheet1')
                                        
                                        if df_players_db is None or df_players_db.empty:
                                            print(f"❌ Google Sheet 'WorldCupU17Data' está vacío o no se pudo cargar")
                                            st.error("⚠️ No se pudo cargar la base de datos de jugadores desde Google Sheets")
                                        else:
                                            print(f"✅ Google Sheet cargado: {len(df_players_db)} jugadores")
                                            print(f"📋 Columnas disponibles: {list(df_players_db.columns)}")
                                            
                                            # Detect column name for player name
                                            name_col = 'PLAYER NAME' if 'PLAYER NAME' in df_players_db.columns else 'Player Name'
                                            print(f"🔎 Buscando en columna: {name_col}")
                                            
                                            # Use PLAYER NAME column from database
                                            player_data_db = df_players_db[df_players_db[name_col].str.strip().str.lower() == selected_player.strip().lower()]
                                            
                                            if player_data_db.empty:
                                                print(f"❌ No se encontró el jugador '{selected_player}' en la base de datos")
                                            else:
                                                print(f"✅ Jugador encontrado! Autocompletando datos...")
                                                
                                                # Get DOB and extract year
                                                dob_value = player_data_db.iloc[0].get('DOB', '')
                                                if pd.notna(dob_value) and str(dob_value).strip():
                                                    birth_year_val = str(dob_value).split('/')[-1] if '/' in str(dob_value) else str(dob_value)[:4]
                                                    try:
                                                        st.session_state.home_match_players[idx]['birth_year'] = int(birth_year_val)
                                                        print(f"  ✓ Año: {birth_year_val}")
                                                    except:
                                                        pass
                                                
                                                # Get Position (POS column) - keep original value
                                                pos_value = player_data_db.iloc[0].get('POS', '')
                                                if pd.notna(pos_value) and str(pos_value).strip():
                                                    pos_raw = str(pos_value).strip()
                                                    st.session_state.home_match_players[idx]['position'] = pos_raw
                                                    print(f"  ✓ Posición: {pos_raw}")
                                                
                                                # Get Number (# column)
                                                number_value = player_data_db.iloc[0].get('#', '')
                                                if pd.notna(number_value):
                                                    try:
                                                        st.session_state.home_match_players[idx]['number'] = int(number_value)
                                                        print(f"  ✓ Número: {number_value}")
                                                    except:
                                                        pass
                                    except Exception as e:
                                        print(f"❌ Error autocompletando datos del jugador: {e}")
                                        import traceback
                                        traceback.print_exc()
                                    
                                    st.rerun()
                            
                            with col2:
                                player_number = st.number_input(
                                    "#",
                                    min_value=1,
                                    max_value=99,
                                    value=player_data.get('number', 1),
                                    key=f"home_p_num_{idx}"
                                )
                                st.session_state.home_match_players[idx]['number'] = player_number
                            
                            with col3:
                                # Auto-fill position - include both general (GK, DF, MF, FW) and specific positions
                                default_pos = ""
                                position_index = 0
                                positions_list = ["", "GK", "DF", "MF", "FW", "RB", "CB", "LB", "DM", "CM", "CAM", "RW", "LW", "ST"]
                                
                                if selected_player:
                                    default_pos = home_player_positions.get(selected_player, "")
                                    if default_pos in positions_list:
                                        position_index = positions_list.index(default_pos)
                                    elif player_data.get('position') in positions_list:
                                        position_index = positions_list.index(player_data['position'])
                                
                                player_position = st.selectbox(
                                    "Position",
                                    positions_list,
                                    index=position_index,
                                    key=f"home_p_pos_{idx}"
                                )
                                st.session_state.home_match_players[idx]['position'] = player_position
                            
                            # Birth Year
                            birth_year = st.number_input(
                                "🎂 AÑO (Birth Year)",
                                min_value=1990,
                                max_value=2015,
                                value=player_data.get('birth_year', 2005),
                                step=1,
                                key=f"home_p_year_{idx}"
                            )
                            st.session_state.home_match_players[idx]['birth_year'] = birth_year
                            
                            # Titular and Minutes
                            col_starter, col_minutes = st.columns(2)
                            
                            with col_starter:
                                starter = st.selectbox(
                                    "🎽 Titular",
                                    ["Sí", "No"],
                                    index=0 if player_data.get('starter', 'Sí') == 'Sí' else 1,
                                    key=f"home_p_starter_{idx}"
                                )
                                st.session_state.home_match_players[idx]['starter'] = starter
                            
                            with col_minutes:
                                minutes = st.number_input(
                                    "⏱️ Minutes",
                                    min_value=0,
                                    max_value=120,
                                    value=player_data.get('minutes', 90),
                                    key=f"home_p_minutes_{idx}"
                                )
                                st.session_state.home_match_players[idx]['minutes'] = minutes
                            
                            # Performance only (Potential removed)
                            performance = st.selectbox(
                                "⚽ Performance (1-6)",
                                [1, 2, 3, 4, 5, 6],
                                index=player_data.get('performance', 1) - 1,
                                key=f"home_p_perf_{idx}"
                            )
                            st.session_state.home_match_players[idx]['performance'] = performance
                            
                            # FIRMAR/CONCLUSION
                            conclusion_options = [
                                "A - Firmar (Sign)",
                                "B+ - Seguir para Firmar (Follow to Sign)",
                                "B - Seguir (Follow)"
                            ]
                            default_conclusion_idx = 0
                            if 'conclusion' in player_data and player_data['conclusion'] in conclusion_options:
                                default_conclusion_idx = conclusion_options.index(player_data['conclusion'])
                            
                            conclusion = st.selectbox(
                                "✅ FIRMAR/CONCLUSION",
                                conclusion_options,
                                index=default_conclusion_idx,
                                key=f"home_p_conclusion_{idx}"
                            )
                            st.session_state.home_match_players[idx]['conclusion'] = conclusion
                            
                            # Report text area
                            report_text = st.text_area(
                                "📝 Report",
                                value=player_data.get('report', ''),
                                height=150,
                                key=f"home_p_report_{idx}"
                            )
                            st.session_state.home_match_players[idx]['report'] = report_text
                            
                            # Remove button
                            if st.button("🗑️ Remove", key=f"remove_home_{idx}"):
                                st.session_state.home_match_players.pop(idx)
                                st.rerun()
                
                # AWAY TEAM PLAYERS
                with col_lineup_away:
                    # Get away team flag emoji
                    away_flag_emoji = COUNTRY_FLAG_EMOJI.get(away_team, '✈️')
                    
                    st.markdown(f"### {away_flag_emoji} {away_team}")
                    
                    # Button to add player
                    if st.button("➕ Add Player" if st.session_state.language == 'en' else "➕ إضافة لاعب", key="add_away_player"):
                        st.session_state.away_match_players.append({
                            'id': len(st.session_state.away_match_players),
                            'name': '',
                            'number': 1,
                            'position': '',
                            'starter': 'Sí',
                            'minutes': 90,
                            'performance': 1,
                            'report': ''
                        })
                        st.rerun()
                    
                    st.markdown("---")
                    
                    # Display added players
                    for idx, player_data in enumerate(st.session_state.away_match_players):
                        # Get current name for display
                        current_name = player_data.get('name', 'Not selected')
                        display_name = current_name if current_name else 'Not selected'
                        
                        with st.expander(f"👤 Player {idx+1}: {display_name}", expanded=True):
                            col1, col2, col3 = st.columns([3, 1, 2])
                            
                            with col1:
                                selected_player = st.selectbox(
                                    "Player Name",
                                    [""] + away_players,
                                    index=0 if not player_data['name'] else (away_players.index(player_data['name']) + 1 if player_data['name'] in away_players else 0),
                                    key=f"away_p_name_{idx}"
                                )
                                # Update name if changed
                                current_name = player_data.get('name', '')
                                if selected_player != current_name:
                                    st.session_state.away_match_players[idx]['name'] = selected_player
                                
                                # Auto-completar datos del jugador cuando se selecciona (siempre que haya jugador)
                                if selected_player and selected_player != current_name:
                                    # 1. Buscar número anterior en reportes previos
                                    try:
                                        prev_reports = read_google_sheet('fifa_u17_match_reports', 'Sheet1')
                                        player_prev_reports = prev_reports[prev_reports['Player Name'] == selected_player]
                                        if not player_prev_reports.empty:
                                            # Obtener el número más reciente
                                            last_number = player_prev_reports.iloc[-1]['Number']
                                            if pd.notna(last_number):
                                                st.session_state.away_match_players[idx]['number'] = int(last_number)
                                    except:
                                        pass
                                    
                                    # 2. Buscar año de nacimiento, posición y número en la base de datos
                                    try:
                                        print(f"🔍 Buscando datos para jugador: {selected_player}")
                                        df_players_db = read_google_sheet('WorldCupU17Data', 'Sheet1')
                                        
                                        if df_players_db is None or df_players_db.empty:
                                            print(f"❌ Google Sheet 'WorldCupU17Data' está vacío o no se pudo cargar")
                                            st.error("⚠️ No se pudo cargar la base de datos de jugadores desde Google Sheets")
                                        else:
                                            print(f"✅ Google Sheet cargado: {len(df_players_db)} jugadores")
                                            print(f"📋 Columnas disponibles: {list(df_players_db.columns)}")
                                            
                                            # Detect column name for player name
                                            name_col = 'PLAYER NAME' if 'PLAYER NAME' in df_players_db.columns else 'Player Name'
                                            print(f"🔎 Buscando en columna: {name_col}")
                                            
                                            # Use PLAYER NAME column from database
                                            player_data_db = df_players_db[df_players_db[name_col].str.strip().str.lower() == selected_player.strip().lower()]
                                            
                                            if player_data_db.empty:
                                                print(f"❌ No se encontró el jugador '{selected_player}' en la base de datos")
                                            else:
                                                print(f"✅ Jugador encontrado! Autocompletando datos...")
                                                
                                                # Get DOB and extract year
                                                dob_value = player_data_db.iloc[0].get('DOB', '')
                                                if pd.notna(dob_value) and str(dob_value).strip():
                                                    birth_year_val = str(dob_value).split('/')[-1] if '/' in str(dob_value) else str(dob_value)[:4]
                                                    try:
                                                        st.session_state.away_match_players[idx]['birth_year'] = int(birth_year_val)
                                                        print(f"  ✓ Año: {birth_year_val}")
                                                    except:
                                                        pass
                                                
                                                # Get Position (POS column) - keep original value
                                                pos_value = player_data_db.iloc[0].get('POS', '')
                                                if pd.notna(pos_value) and str(pos_value).strip():
                                                    pos_raw = str(pos_value).strip()
                                                    st.session_state.away_match_players[idx]['position'] = pos_raw
                                                    print(f"  ✓ Posición: {pos_raw}")
                                                
                                                # Get Number (# column)
                                                number_value = player_data_db.iloc[0].get('#', '')
                                                if pd.notna(number_value):
                                                    try:
                                                        st.session_state.away_match_players[idx]['number'] = int(number_value)
                                                        print(f"  ✓ Número: {number_value}")
                                                    except:
                                                        pass
                                    except Exception as e:
                                        print(f"❌ Error autocompletando datos del jugador: {e}")
                                        import traceback
                                        traceback.print_exc()
                                    
                                    st.rerun()
                            
                            with col2:
                                player_number = st.number_input(
                                    "#",
                                    min_value=1,
                                    max_value=99,
                                    value=player_data.get('number', 1),
                                    key=f"away_p_num_{idx}"
                                )
                                st.session_state.away_match_players[idx]['number'] = player_number
                            
                            with col3:
                                # Auto-fill position - include both general (GK, DF, MF, FW) and specific positions
                                default_pos = ""
                                position_index = 0
                                positions_list = ["", "GK", "DF", "MF", "FW", "RB", "CB", "LB", "DM", "CM", "CAM", "RW", "LW", "ST"]
                                
                                if selected_player:
                                    default_pos = away_player_positions.get(selected_player, "")
                                    if default_pos in positions_list:
                                        position_index = positions_list.index(default_pos)
                                    elif player_data.get('position') in positions_list:
                                        position_index = positions_list.index(player_data['position'])
                                
                                player_position = st.selectbox(
                                    "Position",
                                    positions_list,
                                    index=position_index,
                                    key=f"away_p_pos_{idx}"
                                )
                                st.session_state.away_match_players[idx]['position'] = player_position
                            
                            # Birth Year
                            birth_year_away = st.number_input(
                                "🎂 AÑO (Birth Year)",
                                min_value=1990,
                                max_value=2015,
                                value=player_data.get('birth_year', 2005),
                                step=1,
                                key=f"away_p_year_{idx}"
                            )
                            st.session_state.away_match_players[idx]['birth_year'] = birth_year_away
                            
                            # Titular and Minutes
                            col_starter, col_minutes = st.columns(2)
                            
                            with col_starter:
                                starter = st.selectbox(
                                    "🎽 Titular",
                                    ["Sí", "No"],
                                    index=0 if player_data.get('starter', 'Sí') == 'Sí' else 1,
                                    key=f"away_p_starter_{idx}"
                                )
                                st.session_state.away_match_players[idx]['starter'] = starter
                            
                            with col_minutes:
                                minutes = st.number_input(
                                    "⏱️ Minutes",
                                    min_value=0,
                                    max_value=120,
                                    value=player_data.get('minutes', 90),
                                    key=f"away_p_minutes_{idx}"
                                )
                                st.session_state.away_match_players[idx]['minutes'] = minutes
                            
                            # Performance only (Potential removed)
                            performance = st.selectbox(
                                "⚽ Performance (1-6)",
                                [1, 2, 3, 4, 5, 6],
                                index=player_data.get('performance', 1) - 1,
                                key=f"away_p_perf_{idx}"
                            )
                            st.session_state.away_match_players[idx]['performance'] = performance
                            
                            # FIRMAR/CONCLUSION
                            conclusion_options_away = [
                                "A - Firmar (Sign)",
                                "B+ - Seguir para Firmar (Follow to Sign)",
                                "B - Seguir (Follow)"
                            ]
                            default_conclusion_idx_away = 0
                            if 'conclusion' in player_data and player_data['conclusion'] in conclusion_options_away:
                                default_conclusion_idx_away = conclusion_options_away.index(player_data['conclusion'])
                            
                            conclusion_away = st.selectbox(
                                "✅ FIRMAR/CONCLUSION",
                                conclusion_options_away,
                                index=default_conclusion_idx_away,
                                key=f"away_p_conclusion_{idx}"
                            )
                            st.session_state.away_match_players[idx]['conclusion'] = conclusion_away
                            
                            # Report text area
                            report_text = st.text_area(
                                "📝 Report",
                                value=player_data.get('report', ''),
                                height=150,
                                key=f"away_p_report_{idx}"
                            )
                            st.session_state.away_match_players[idx]['report'] = report_text
                            
                            # Remove button
                            if st.button("🗑️ Remove", key=f"remove_away_{idx}"):
                                st.session_state.away_match_players.pop(idx)
                                st.rerun()
                
                st.markdown("---")
                
                # Save button
                if st.button("💾 Save Match Report" if st.session_state.language == 'en' else "💾 حفظ تقرير المباراة", type="primary"):
                    if not scout_name or not match_phase:
                        st.error("Please fill all required fields" if st.session_state.language == 'en' else "يرجى ملء جميع الحقول المطلوبة")
                    elif len(st.session_state.home_match_players) == 0 and len(st.session_state.away_match_players) == 0:
                        st.warning("⚠️ Please add at least one player" if st.session_state.language == 'en' else "⚠️ يرجى إضافة لاعب واحد على الأقل")
                    else:
                        # Prepare player reports for saving
                        player_reports_list = []
                        
                        # Add home team players
                        for player in st.session_state.home_match_players:
                            if player['name']:  # Only save if player is selected
                                player_reports_list.append({
                                    'Date': str(match_date),
                                    'Scout': scout_name,
                                    'Phase': match_phase,
                                    'Match': f"{home_team} vs {away_team}",
                                    'Team': home_team,
                                    'Player Name': player['name'],
                                    'Number': player['number'],
                                    'Position': player['position'],
                                    'Birth Year': player.get('birth_year', ''),
                                    'Starter': player['starter'],
                                    'Minutes': player['minutes'],
                                    'Performance': player['performance'],
                                    'Conclusion': player.get('conclusion', 'B - Seguir (Follow)'),
                                    'Report': player['report']
                                })
                        
                        # Add away team players
                        for player in st.session_state.away_match_players:
                            if player['name']:  # Only save if player is selected
                                player_reports_list.append({
                                    'Date': str(match_date),
                                    'Scout': scout_name,
                                    'Phase': match_phase,
                                    'Match': f"{home_team} vs {away_team}",
                                    'Team': away_team,
                                    'Player Name': player['name'],
                                    'Number': player['number'],
                                    'Position': player['position'],
                                    'Birth Year': player.get('birth_year', ''),
                                    'Starter': player['starter'],
                                    'Minutes': player['minutes'],
                                    'Performance': player['performance'],
                                    'Conclusion': player.get('conclusion', 'B - Seguir (Follow)'),
                                    'Report': player['report']
                                })
                        
                        if player_reports_list:
                            # Save to Google Sheets (with local Excel fallback)
                            try:
                                df_new_reports = pd.DataFrame(player_reports_list)
                                
                                # Append to Google Sheet
                                result = append_to_google_sheet(df_new_reports, 'fifa_u17_match_reports', 'Sheet1')
                                
                                if result:
                                    st.success(f"✅ Match report saved! {len(player_reports_list)} player reports added." if st.session_state.language == 'en' else f"✅ تم حفظ تقرير المباراة! تم إضافة {len(player_reports_list)} تقرير لاعب.")
                                    st.balloons()
                                    
                                    # Clear session state
                                    st.session_state.home_match_players = []
                                    st.session_state.away_match_players = []
                                    st.rerun()
                                else:
                                    st.error("❌ Error: No se pudo guardar en Google Sheets. Verifica las credenciales.")
                                    st.info("💡 Revisa que el Google Sheet 'fifa_u17_match_reports' exista y esté compartido con el service account.")
                                
                            except Exception as e:
                                st.error(f"❌ Error saving report: {e}")
                                st.warning("⚠️ Si otro scout está guardando informes, espera unos segundos e intenta de nuevo.")
                                import traceback
                                st.code(traceback.format_exc())
                        else:
                            st.warning("⚠️ No players selected to save" if st.session_state.language == 'en' else "⚠️ لا يوجد لاعبون محددون للحفظ")
            
            except FileNotFoundError:
                st.error("❌ WorldCupU17Data.xlsx file not found" if st.session_state.language == 'en' else "❌ ملف WorldCupU17Data.xlsx غير موجود")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.info("👆 Please select both home and away teams to configure lineups" if st.session_state.language == 'en' else "👆 يرجى اختيار الفريق المحلي والزائر لإعداد التشكيلات")
    
    # Tab 1: CREATE INDIVIDUAL REPORT
    with tabs[1]:
        # Load Al Nassr logo for title
        try:
            from PIL import Image
            import io
            logo_ind = Image.open('alnassr.png')
            logo_ind.thumbnail((30, 30))
            buffered_ind = io.BytesIO()
            if logo_ind.mode in ('RGBA', 'LA', 'P'):
                logo_ind.save(buffered_ind, format="PNG")
            else:
                logo_ind = logo_ind.convert('RGB')
                logo_ind.save(buffered_ind, format="PNG")
            logo_ind_str = base64.b64encode(buffered_ind.getvalue()).decode()
            logo_ind_html = f'<img src="data:image/png;base64,{logo_ind_str}" style="height:24px; vertical-align:middle; margin-right:8px;">'
        except:
            logo_ind_html = '👤'
        
        st.markdown(f"### {logo_ind_html} Create Individual Player Report", unsafe_allow_html=True)
        
        # Load player database
        try:
            df_players = read_google_sheet('WorldCupU17Data', 'Sheet1')
            if df_players.empty:
                df_players = pd.read_excel('WorldCupU17Data.xlsx')
            
            # Detectar nombres de columnas
            country_col_ind = None
            for col in df_players.columns:
                if col.lower() in ['país', 'pais', 'country', 'equipo', 'team']:
                    country_col_ind = col
                    break
            
            position_col_ind = None
            for col in df_players.columns:
                if 'position' in col.lower() or 'posición' in col.lower():
                    position_col_ind = col
                    break
            
            name_col_ind = None
            for col in df_players.columns:
                if col.lower() in ['nombre', 'name', 'player']:
                    name_col_ind = col
                    break
            
            # Team selection
            st.markdown("---")
            teams = sorted(df_players[country_col_ind].unique().tolist())
            selected_team = st.selectbox(
                "🌍 Select Team / Selección",
                [""] + teams,
                key="individual_team_select"
            )
            
            if selected_team:
                # Filter players by team
                team_players = df_players[df_players[country_col_ind] == selected_team].copy()
                
                # Sort by position order (GK first, ST last)
                position_order = {'Portero': 1, 'Lateral Derecho': 2, 'Lateral Izquierdo': 3, 'Defensa Central': 4, 
                                'Pivote': 5, 'Mediocentro': 6, 'Mediocentro Ofensivo': 7, 
                                'Extremo Derecho': 8, 'Extremo Izquierdo': 9, 'Delantero Centro': 10}
                team_players['pos_order'] = team_players[position_col_ind].map(position_order).fillna(99)
                team_players = team_players.sort_values('pos_order')
                
                player_names = team_players[name_col_ind].tolist()
                
                selected_player = st.selectbox(
                    "👤 Select Player / Jugador",
                    [""] + player_names,
                    key="individual_player_select"
                )
                
                if selected_player:
                    # Get player data
                    player_data = team_players[team_players[name_col_ind] == selected_player].iloc[0]
                    
                    st.markdown("---")
                    st.markdown("### 📋 Player Information")
                    
                    # Display auto-filled data
                    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                    
                    with col_info1:
                        st.markdown(f"**Name:** {player_data.get(name_col_ind, 'N/A')}")
                    with col_info2:
                        st.markdown(f"**Position:** {player_data.get(position_col_ind, 'N/A')}")
                    with col_info3:
                        birth_date = str(player_data.get('Año', 'N/A'))[:10]  # Remove time if present
                        st.markdown(f"**Birth Date:** {birth_date}")
                    with col_info4:
                        contract = str(player_data.get('Fin Contrato', 'N/A'))[:10]  # Remove time
                        st.markdown(f"**Contract:** {contract}")
                    
                    st.markdown("---")
                    st.markdown("### 📝 Additional Information")
                    
                    # Scout name - Default to SCOUTING DEPARTMENT
                    scout_name = st.selectbox(
                        "👤 Scout Name / Nombre del Scout",
                        options=["SCOUTING DEPARTMENT", "Juan Gambero", "Alvaro Lopez", "Rafa Gil"],
                        index=0,  # Default to SCOUTING DEPARTMENT
                        key="ind_scout_name"
                    )
                    
                    # Agent info
                    col_agent1, col_agent2 = st.columns(2)
                    with col_agent1:
                        agent_name = st.text_input("🤝 Agent Name / Nombre del Agente", key="ind_agent_name")
                    with col_agent2:
                        agent_phone = st.text_input("📞 Agent Phone / Teléfono del Agente", key="ind_agent_phone")
                    
                    # Check if player already has a photo in previous reports
                    existing_photo_path = None
                    try:
                        df_existing_reports = read_google_sheet('fifa_u17_individual_reports', 'Sheet1')
                        player_reports = df_existing_reports[df_existing_reports['Player'] == selected_player]
                        if not player_reports.empty:
                            # Get the most recent report with a photo
                            for idx, report in player_reports.iterrows():
                                if report.get('Photo') and str(report['Photo']) != 'nan' and str(report['Photo']).strip():
                                    existing_photo_path = report['Photo']
                                    break
                    except:
                        pass
                    
                    # Show existing photo if available
                    if existing_photo_path:
                        st.info(f"📸 Este jugador ya tiene una foto guardada. Se usará automáticamente.")
                        try:
                            from PIL import Image
                            existing_img = Image.open(existing_photo_path)
                            st.image(existing_img, width=200, caption=f"Foto actual de {selected_player}")
                        except:
                            st.warning("⚠️ No se pudo cargar la foto guardada. Puedes subir una nueva.")
                            existing_photo_path = None
                    
                    # Photo upload
                    uploaded_photo = st.file_uploader(
                        "📷 Upload New Player Photo / Subir Nueva Foto del Jugador" if existing_photo_path else "📷 Upload Player Photo / Subir Foto del Jugador",
                        type=['jpg', 'jpeg', 'png'],
                        key="ind_photo_upload",
                        help="Sube una nueva foto solo si quieres cambiar la actual" if existing_photo_path else None
                    )
                    
                    if uploaded_photo:
                        st.success("✅ Nueva foto subida correctamente")
                    
                    st.markdown("---")
                    st.markdown("### ⚙️ Technical Evaluation")
                    
                    # Technical ratings
                    col_eval1, col_eval2, col_eval3 = st.columns(3)
                    
                    # Helper functions for colors
                    def get_color_for_value(value):
                        if value <= 2:
                            return "#FF4444"  # Red
                        elif value <= 4:
                            return "#FFA500"  # Orange
                        else:
                            return "#00C851"  # Green
                    
                    def get_color_for_perfil(perfil_text):
                        if "TOP WORLD CLASS" in perfil_text:
                            return "#00C851"  # Green
                        elif "ELITE CHAMPIONS LEAGUE" in perfil_text:
                            return "#4285F4"  # Blue
                        elif "FIRST PRO LEVEL" in perfil_text:
                            return "#8B4513"  # Brown
                        else:
                            return "#FFA500"  # Orange
                    
                    with col_eval1:
                        rendimiento = st.selectbox(
                            "🎯 Rendimiento (Performance)",
                            [1, 2, 3, 4, 5, 6],
                            index=2,
                            key="ind_rendimiento"
                        )
                        rend_color = get_color_for_value(rendimiento)
                        rend_pct = (rendimiento / 6) * 100
                        st.markdown(f'''
                            <div style="background-color: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;">
                                <div style="background-color: {rend_color}; height: 100%; width: {rend_pct}%; border-radius: 10px;"></div>
                            </div>
                        ''', unsafe_allow_html=True)
                    
                    with col_eval2:
                        potencial = st.selectbox(
                            "⭐ Potencial (Potential)",
                            [1, 2, 3, 4, 5, 6],
                            index=2,
                            key="ind_potencial"
                        )
                        pot_color = get_color_for_value(potencial)
                        pot_pct = (potencial / 6) * 100
                        st.markdown(f'''
                            <div style="background-color: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;">
                                <div style="background-color: {pot_color}; height: 100%; width: {pot_pct}%; border-radius: 10px;"></div>
                            </div>
                        ''', unsafe_allow_html=True)
                    
                    with col_eval3:
                        perfil_options = [
                            "1 - BACKUP SPL - TOP 4",
                            "2 - STARTER SPL - TOP 4",
                            "3 - STAND OUT SPL - TOP4",
                            "4 - FIRST PRO LEVEL",
                            "5 - ELITE CHAMPIONS LEAGUE",
                            "6 - TOP WORLD CLASS"
                        ]
                        perfil_selected = st.selectbox(
                            "📊 Perfil (Profile)",
                            perfil_options,
                            index=2,
                            key="ind_perfil"
                        )
                        # Extract numeric value
                        perfil = int(perfil_selected.split(' - ')[0])
                        perfil_color = get_color_for_perfil(perfil_selected)
                        perfil_pct = (perfil / 6) * 100
                        st.markdown(f'''
                            <div style="background-color: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;">
                                <div style="background-color: {perfil_color}; height: 100%; width: {perfil_pct}%; border-radius: 10px;"></div>
                            </div>
                        ''', unsafe_allow_html=True)
                    
                    # Technical comment
                    comentario_tecnico = st.text_area(
                        "💬 Technical Comment / Comentario Técnico",
                        height=150,
                        placeholder="Enter detailed technical evaluation...",
                        key="ind_comentario"
                    )
                    
                    st.markdown("---")
                    st.markdown("### 📌 Conclusion")
                    
                    conclusion = st.radio(
                        "Final Decision / Decisión Final",
                        ["A - Firmar (Sign)", "B+ - Seguir para Firmar (Follow to Sign)", "B - Seguir (Follow)"],
                        key="ind_conclusion"
                    )
                    
                    st.markdown("---")
                    
                    # Save button
                    if st.button("💾 Save Individual Report", type="primary", use_container_width=True):
                        # Prepare report data
                        report_data = {
                            'Date': date.today().strftime('%Y-%m-%d'),
                            'Scout': scout_name,
                            'Team': selected_team,
                            'Player': selected_player,
                            'Position': player_data.get('Position principal', 'N/A'),
                            'Birth Date': birth_date,
                            'Contract': contract,
                            'Agent': agent_name,
                            'Agent Phone': agent_phone,
                            'Rendimiento': rendimiento,
                            'Potencial': potencial,
                            'Perfil': perfil_selected,  # Save full description
                            'Technical Comment': comentario_tecnico,
                            'Conclusion': conclusion
                        }
                        
                        # Save photo: use new uploaded photo, or keep existing one
                        if uploaded_photo:
                            # Create directory if it doesn't exist
                            import os
                            os.makedirs('player_photos', exist_ok=True)
                            
                            # Save photo to disk
                            photo_filename = f"player_photos/{selected_player.replace(' ', '_')}.jpg"
                            with open(photo_filename, 'wb') as f:
                                f.write(uploaded_photo.getbuffer())
                            report_data['Photo'] = photo_filename
                        elif existing_photo_path:
                            # Use existing photo from previous report
                            report_data['Photo'] = existing_photo_path
                        else:
                            report_data['Photo'] = ''
                        
                        # Save to Google Sheets (with local Excel fallback)
                        try:
                            df_individual = pd.DataFrame([report_data])
                            
                            # Append to Google Sheet
                            result = append_to_google_sheet(df_individual, 'fifa_u17_individual_reports', 'Sheet1')
                            
                            if result:
                                st.success("✅ Individual report saved successfully!")
                                st.balloons()
                                # Clear cache to show new data immediately
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Error: No se pudo guardar el informe en Google Sheets")
                                st.warning("⚠️ Verifica que el Google Sheet 'fifa_u17_individual_reports' exista y tengas permisos de escritura.")
                        except Exception as e:
                            st.error(f"❌ Error saving report: {e}")
                            st.warning("⚠️ Si otro scout está guardando informes, espera unos segundos e intenta de nuevo.")
                            import traceback
                            st.code(traceback.format_exc())
        
        except FileNotFoundError:
            st.error("❌ WorldCupU17Data.xlsx not found. Please add the player database file.")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Tab 3: VIEW INDIVIDUAL REPORTS (content from old tab 2)
    with tabs[3]:
        # Load Al Nassr logo for title
        try:
            from PIL import Image
            import io
            logo_img = Image.open('alnassr.png')
            logo_img.thumbnail((40, 40))
            buffered = io.BytesIO()
            if logo_img.mode in ('RGBA', 'LA', 'P'):
                logo_img.save(buffered, format="PNG")
            else:
                logo_img = logo_img.convert('RGB')
                logo_img.save(buffered, format="PNG")
            logo_str = base64.b64encode(buffered.getvalue()).decode()
            logo_html = f'<img src="data:image/png;base64,{logo_str}" style="height:32px; vertical-align:middle; margin-right:10px;">'
        except:
            logo_html = '📋'  # Fallback to emoji if logo not found
        
        st.markdown(f"<h2 style='text-align: center; color: #002B5B;'>{logo_html} INDIVIDUAL REPORTS</h2>", unsafe_allow_html=True)
        
        try:
            # Load individual reports
            df_individual_reports = read_google_sheet('fifa_u17_individual_reports', 'Sheet1')
            
            # Check if navigated from player database
            filter_player_name = st.session_state.get('filter_player', None)
            if filter_player_name:
                st.info(f"👤 Showing reports for: **{filter_player_name}**")
                # Clear the filter after showing
                if st.button("❌ Clear Filter"):
                    st.session_state.filter_player = None
                    st.rerun()
            
            if not df_individual_reports.empty:
                # Filters
                st.markdown("---")
                st.markdown("🔍 **Filtros / Filters**")
                col_f1, col_f2, col_f3 = st.columns(3)
                
                # Use all reports for filters
                filtered_reports = df_individual_reports.copy()
                base_df_for_filters = df_individual_reports
                
                with col_f1:
                    scouts_filter = ['All Scouts'] + sorted(base_df_for_filters['Scout'].dropna().unique().tolist())
                    selected_scout_filter = st.selectbox("👤 Scout", scouts_filter, key="ind_reports_scout_filter")
                
                with col_f2:
                    # Filtrar equipos según el scout seleccionado
                    if selected_scout_filter != 'All Scouts':
                        available_teams = base_df_for_filters[base_df_for_filters['Scout'] == selected_scout_filter]['Team'].unique()
                    else:
                        available_teams = base_df_for_filters['Team'].unique()
                    teams_filter = ['All Teams'] + sorted(available_teams.tolist())
                    selected_team_filter = st.selectbox("🌍 Team", teams_filter, key="ind_reports_team_filter")
                
                with col_f3:
                    # Filtrar jugadores según scout y equipo seleccionados
                    filtered_for_players = base_df_for_filters.copy()
                    if selected_scout_filter != 'All Scouts':
                        filtered_for_players = filtered_for_players[filtered_for_players['Scout'] == selected_scout_filter]
                    if selected_team_filter != 'All Teams':
                        filtered_for_players = filtered_for_players[filtered_for_players['Team'] == selected_team_filter]
                    
                    players_filter = ['All Players'] + sorted(filtered_for_players['Player'].unique().tolist())
                    # Auto-select player if navigated from player database
                    default_player_index = 0
                    if filter_player_name and filter_player_name in players_filter:
                        default_player_index = players_filter.index(filter_player_name)
                    selected_player_filter = st.selectbox("👤 Player", players_filter, index=default_player_index, key="ind_reports_player_filter")
                
                # Apply manual filters on top of intelligent search results
                if selected_scout_filter != 'All Scouts':
                    filtered_reports = filtered_reports[filtered_reports['Scout'] == selected_scout_filter]
                if selected_team_filter != 'All Teams':
                    filtered_reports = filtered_reports[filtered_reports['Team'] == selected_team_filter]
                if selected_player_filter != 'All Players':
                    filtered_reports = filtered_reports[filtered_reports['Player'] == selected_player_filter]
                
                st.markdown("---")
                
                # Download buttons for Individual Reports
                st.markdown("### 📥 Descargar Datos / Download Data")
                create_download_buttons(
                    filtered_reports, 
                    filename_base="fifa_u17_individual_reports",
                    label_prefix="Descargar / Download"
                )
                st.markdown("---")
                
                # === VISUALIZACIÓN DE MEDIAS SI UN JUGADOR TIENE MÚLTIPLES INFORMES ===
                if selected_player_filter != 'All Players':
                    player_reports = filtered_reports[filtered_reports['Player'] == selected_player_filter]
                    unique_scouts = player_reports['Scout'].nunique()
                    
                    if unique_scouts >= 2:
                        st.markdown(f"### 📊 {selected_player_filter} - Media de {unique_scouts} Scouts")
                        st.markdown("")
                        
                        # Calcular medias (convertir a numérico, ignorando valores no numéricos)
                        avg_rendimiento = pd.to_numeric(player_reports['Rendimiento'], errors='coerce').mean()
                        avg_potencial = pd.to_numeric(player_reports['Potencial'], errors='coerce').mean()
                        
                        # Mostrar medias en 2 columnas con número grande y barra de progreso
                        col_avg1, col_avg2 = st.columns(2)
                        
                        with col_avg1:
                            st.markdown("""
                                <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); text-align: center;">
                                    <p style="font-size: 14px; color: #999; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">🎯 RENDIMIENTO - MEDIA</p>
                                    <h1 style="font-size: 72px; font-weight: 700; color: #1B2845; margin: 10px 0; line-height: 1;">{:.1f}</h1>
                                    <p style="font-size: 14px; color: #666; margin-top: 5px;">Sobre 6.0</p>
                                </div>
                            """.format(avg_rendimiento), unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                            progress_rend = avg_rendimiento / 6.0
                            st.progress(progress_rend)
                        
                        with col_avg2:
                            st.markdown("""
                                <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); text-align: center;">
                                    <p style="font-size: 14px; color: #999; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">⭐ POTENCIAL - MEDIA</p>
                                    <h1 style="font-size: 72px; font-weight: 700; color: #1B2845; margin: 10px 0; line-height: 1;">{:.1f}</h1>
                                    <p style="font-size: 14px; color: #666; margin-top: 5px;">Sobre 6.0</p>
                                </div>
                            """.format(avg_potencial), unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                            progress_pot = avg_potencial / 6.0
                            st.progress(progress_pot)
                        
                        st.markdown("---")
                        st.markdown(f"### 📝 Detalles de {len(player_reports)} Informes Individuales")
                    else:
                        st.markdown(f"### 📊 {len(filtered_reports)} Individual Report(s)")
                else:
                    st.markdown(f"### 📊 {len(filtered_reports)} Individual Report(s)")
                
                # Display reports
                for idx, report in filtered_reports.iterrows():
                    # Get scout name if available
                    scout_name = report.get('Scout', 'Unknown')
                    player_name = report['Player']
                    team = report['Team']
                    conclusion = report.get('Conclusion', '')
                    report_date = report.get('Date', 'N/A')
                    
                    with st.expander(
                        f"👤 {player_name} ({team}) | {conclusion} | 📅 {report_date} | 👤 Scout: {scout_name}",
                        expanded=False
                    ):
                        # === PROFESSIONAL SCOUTING CARD CSS ===
                        st.markdown("""
                            <style>
                            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
                            body { background-color: #fafafa; font-family: 'Inter', sans-serif; }
                            
                            .scouting-card-header {
                                background: linear-gradient(135deg, #1B2845 0%, #0d1421 100%);
                                color: white;
                                padding: 20px 30px;
                                border-radius: 8px 8px 0 0;
                                margin: -10px -10px 20px -10px;
                            }
                            .header-content {
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                flex-wrap: wrap;
                                gap: 15px;
                                font-size: 15px;
                                font-weight: 600;
                            }
                            
                            .player-photo-pro { 
                                width: 150px; 
                                height: 150px; 
                                border-radius: 50%; 
                                border: 4px solid #FFD700; 
                                object-fit: cover; 
                                margin: 0 auto 15px auto; 
                                display: block;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                            }
                            .player-name-pro { 
                                font-size: 22px; 
                                font-weight: 700; 
                                color: #1a2332; 
                                text-align: center; 
                                margin: 10px 0 5px 0; 
                            }
                            .player-info-pro { 
                                font-size: 13px; 
                                color: #666; 
                                text-align: center;
                            }
                            
                            .metric-card-pro { 
                                background: white; 
                                padding: 25px 15px; 
                                border-radius: 8px; 
                                box-shadow: 0 2px 10px rgba(0,0,0,0.08); 
                                text-align: center;
                                height: 100%;
                            }
                            .metric-value-pro { 
                                font-size: 56px; 
                                font-weight: 700; 
                                color: #1a2332; 
                                line-height: 1; 
                                margin-bottom: 10px;
                            }
                            .metric-label-pro { 
                                font-size: 11px; 
                                color: #999; 
                                text-transform: uppercase; 
                                letter-spacing: 2px; 
                                margin-bottom: 15px;
                                font-weight: 600;
                            }
                            .stars-pro { 
                                font-size: 22px; 
                                display: flex; 
                                justify-content: center; 
                                gap: 3px;
                            }
                            .profile-text-pro {
                                font-size: 16px;
                                font-weight: 600;
                                color: #1a2332;
                                margin-top: 10px;
                                line-height: 1.4;
                            }
                            .star-gold { color: #FFD700; }
                            .star-gray { color: #e0e0e0; }
                            
                            .info-bar-pro {
                                background: white;
                                padding: 18px 20px;
                                border-radius: 0;
                                border-top: 1px solid #e0e0e0;
                                border-bottom: 1px solid #e0e0e0;
                                display: flex;
                                justify-content: space-around;
                                gap: 20px;
                                flex-wrap: wrap;
                                margin: 20px 0;
                            }
                            .info-bar-pro span {
                                font-size: 13px;
                                color: #495057;
                                font-weight: 500;
                            }
                            
                            .report-box-pro {
                                background: #fffef0;
                                padding: 25px;
                                border-radius: 5px;
                                border-left: 5px solid #FFC107;
                                margin-bottom: 20px;
                            }
                            .report-text-pro {
                                font-style: italic;
                                color: #333;
                                font-size: 16px;
                                margin: 0;
                                line-height: 1.8;
                            }
                            
                            .action-button-pro {
                                background: linear-gradient(135deg, #28a745 0%, #218838 100%);
                                color: white;
                                padding: 25px;
                                text-align: center;
                                border-radius: 8px;
                                box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
                            }
                            .action-button-pro.orange {
                                background: linear-gradient(135deg, #ff8c00 0%, #e67e00 100%);
                                box-shadow: 0 4px 15px rgba(255, 140, 0, 0.3);
                            }
                            .action-button-pro.blue {
                                background: linear-gradient(135deg, #1B2845 0%, #0d1421 100%);
                                box-shadow: 0 4px 15px rgba(27, 40, 69, 0.3);
                            }
                            .action-text-pro {
                                font-size: 28px;
                                font-weight: 700;
                                text-transform: uppercase;
                                letter-spacing: 2px;
                                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
                                margin: 0;
                            }
                            
                            @keyframes fadeInUp {
                                from {
                                    opacity: 0;
                                    transform: translateY(20px);
                                }
                                to {
                                    opacity: 1;
                                    transform: translateY(0);
                                }
                            }
                            .animate-fade-in {
                                animation: fadeInUp 0.6s ease-out;
                            }
                            </style>
                        """, unsafe_allow_html=True)
                        
                        # Get data for the report
                        birth_year = str(report['Birth Date'])[:4] if report.get('Birth Date') else 'N/A'
                        position = report.get('Position', 'N/A')
                        contract = report.get('Contract', 'N/A')
                        agent = report.get('Agent', 'N/A')
                        phone = report.get('Agent Phone', 'N/A')
                        tech_comment = report.get('Technical Comment', 'No technical comment available.')
                        
                        # Get flag emoji
                        flag_emoji = COUNTRY_FLAG_EMOJI.get(team, '🏴')
                        flag_html = f'<span style="font-size:18px; margin-right:8px;">{flag_emoji}</span>'
                        
                        # === RED HEADER ===
                        st.markdown(f"""
                            <div class="scouting-card-header">
                                <div class="header-content">
                                    <div>{flag_html}<strong>{player_name}</strong> | {team}</div>
                                    <div>📅 {report_date} | 👤 {scout_name}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # === 4 COLUMNS SECTION ===
                        col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1.3])
                        
                        # COLUMN 1: Photo + Name + Info
                        with col1:
                            # Try to find player photo
                            photo_path = None
                            
                            try:
                                # PRIORITY 1: Try to find photo locally first
                                found_path = find_player_photo(player_name)
                                if found_path and os.path.exists(found_path):
                                    photo_path = found_path
                                else:
                                    # PRIORITY 2: Try the path from Google Sheets
                                    if report.get('Photo') and report['Photo']:
                                        photo_source = report['Photo']
                                        
                                        # Check if it's a URL (GitHub) or local path
                                        if photo_source.startswith('http'):
                                            # It's already a URL
                                            photo_path = photo_source
                                        else:
                                            # It's a local path - check if file exists locally
                                            if os.path.exists(photo_source):
                                                # Local file exists
                                                photo_path = photo_source
                                            else:
                                                # File doesn't exist locally
                                                # Try different extensions for the same base filename
                                                import os.path as osp
                                                base_path = osp.splitext(photo_source)[0]  # Remove extension
                                                extensions = ['.jpg', '.png', '.jpeg', '.JPG', '.PNG', '.JPEG']
                                                
                                                # Try each extension locally first
                                                for ext in extensions:
                                                    test_path = base_path + ext
                                                    if os.path.exists(test_path):
                                                        photo_path = test_path
                                                        break
                                                
                                                # PRIORITY 3: If still not found, try GitHub URL
                                                if not photo_path:
                                                    github_base = "https://raw.githubusercontent.com/alvarolopez8810/alnassrscoutingsystem/main/"
                                                    photo_path = github_base + photo_source
                                    else:
                                        # PRIORITY 4: Last resort - try GitHub URLs with different name variations
                                        possible_urls = find_player_photo_github(player_name)
                                        if possible_urls:
                                            photo_path = possible_urls[0]
                            except Exception:
                                # If os operations fail, try to construct GitHub URL
                                try:
                                    if report.get('Photo') and report['Photo']:
                                        photo_source = report['Photo']
                                        if not photo_source.startswith('http'):
                                            github_base = "https://raw.githubusercontent.com/alvarolopez8810/alnassrscoutingsystem/main/"
                                            photo_path = github_base + photo_source
                                except:
                                    photo_path = None
                            
                            # Display photo or fallback
                            if photo_path:
                                photo_loaded = False
                                from PIL import Image
                                import io
                                
                                # Check if photo_path is a URL or local file
                                if photo_path.startswith('http'):
                                    # Try to download from URL
                                    import requests
                                    
                                    # Get all possible URLs to try
                                    urls_to_try = [photo_path]
                                    
                                    # Also try different extensions for the same base URL
                                    import os.path as osp
                                    base_url = osp.splitext(photo_path)[0]
                                    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
                                    for ext in extensions:
                                        test_url = base_url + ext
                                        if test_url not in urls_to_try:
                                            urls_to_try.append(test_url)
                                    
                                    # If first URL fails, try other variations based on player name
                                    if not photo_loaded:
                                        possible_urls = find_player_photo_github(player_name)
                                        urls_to_try.extend([url for url in possible_urls if url not in urls_to_try])
                                    
                                    for url in urls_to_try:
                                        try:
                                            response = requests.get(url, timeout=5)
                                            if response.status_code == 200:
                                                img = Image.open(io.BytesIO(response.content))
                                                buffered = io.BytesIO()
                                                if img.mode in ('RGBA', 'LA', 'P'):
                                                    img.save(buffered, format="PNG")
                                                else:
                                                    img = img.convert('RGB')
                                                    img.save(buffered, format="PNG")
                                                img_str = base64.b64encode(buffered.getvalue()).decode()
                                                st.markdown(f'<img src="data:image/png;base64,{img_str}" class="player-photo-pro">', unsafe_allow_html=True)
                                                photo_loaded = True
                                                break
                                        except:
                                            continue
                                else:
                                    # Try to open local file
                                    try:
                                        img = Image.open(photo_path)
                                        buffered = io.BytesIO()
                                        if img.mode in ('RGBA', 'LA', 'P'):
                                            img.save(buffered, format="PNG")
                                        else:
                                            img = img.convert('RGB')
                                            img.save(buffered, format="PNG")
                                        img_str = base64.b64encode(buffered.getvalue()).decode()
                                        st.markdown(f'<img src="data:image/png;base64,{img_str}" class="player-photo-pro">', unsafe_allow_html=True)
                                        photo_loaded = True
                                    except:
                                        pass
                                
                                # If photo still not loaded, show fallback
                                if not photo_loaded:
                                    # Fallback to Al Nassr logo
                                    try:
                                        from PIL import Image
                                        import io
                                        logo_img = Image.open('alnassr.png')
                                        buffered = io.BytesIO()
                                        if logo_img.mode in ('RGBA', 'LA', 'P'):
                                            logo_img.save(buffered, format="PNG")
                                        else:
                                            logo_img = logo_img.convert('RGB')
                                            logo_img.save(buffered, format="PNG")
                                        logo_str = base64.b64encode(buffered.getvalue()).decode()
                                        st.markdown(f'<img src="data:image/png;base64,{logo_str}" class="player-photo-pro">', unsafe_allow_html=True)
                                    except:
                                        st.markdown('<div style="width:150px; height:150px; border-radius:50%; border:4px solid #FFD700; display:flex; align-items:center; justify-content:center; margin:0 auto; background:#f0f0f0; font-size:60px;">👤</div>', unsafe_allow_html=True)
                            else:
                                # No photo found, use Al Nassr logo
                                try:
                                    from PIL import Image
                                    import io
                                    logo_img = Image.open('alnassr.png')
                                    buffered = io.BytesIO()
                                    if logo_img.mode in ('RGBA', 'LA', 'P'):
                                        logo_img.save(buffered, format="PNG")
                                    else:
                                        logo_img = logo_img.convert('RGB')
                                        logo_img.save(buffered, format="PNG")
                                    logo_str = base64.b64encode(buffered.getvalue()).decode()
                                    st.markdown(f'<img src="data:image/png;base64,{logo_str}" class="player-photo-pro">', unsafe_allow_html=True)
                                except:
                                    st.markdown('<div style="width:150px; height:150px; border-radius:50%; border:4px solid #FFD700; display:flex; align-items:center; justify-content:center; margin:0 auto; background:#f0f0f0; font-size:60px;">👤</div>', unsafe_allow_html=True)
                            
                            # Nombre
                            st.markdown(f'<p class="player-name-pro">{report["Player"]}</p>', unsafe_allow_html=True)
                            
                            # Subtítulo con posición, año, país y bandera
                            birth_year = str(report['Birth Date'])[:4] if report.get('Birth Date') else 'N/A'
                            position = report.get('Position', 'N/A')
                            team = report['Team']
                            
                            # Get country flag emoji
                            flag_emoji = COUNTRY_FLAG_EMOJI.get(team, '🏴')
                            
                            st.markdown(f'<p class="player-info-pro">{position} • {birth_year} • {flag_emoji} {team}</p>', unsafe_allow_html=True)
                        
                        # COLUMN 2: Performance
                        with col2:
                            try:
                                rendimiento = int(float(report['Rendimiento']))
                            except (ValueError, TypeError):
                                rendimiento = 0
                            stars_html = ''.join([f'<span class="star-gold">⭐</span>' for _ in range(rendimiento)]) + ''.join([f'<span class="star-gray">☆</span>' for _ in range(6 - rendimiento)])
                            st.markdown(f"""
                                <div class="metric-card-pro animate-fade-in">
                                    <div class="metric-value-pro">{rendimiento if rendimiento > 0 else '-'}</div>
                                    <div class="metric-label-pro">Rendimiento</div>
                                    <div class="stars-pro">{stars_html}</div>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # COLUMN 3: Potential
                        with col3:
                            try:
                                potencial = int(float(report['Potencial']))
                            except (ValueError, TypeError):
                                potencial = 0
                            stars_html = ''.join([f'<span class="star-gold">⭐</span>' for _ in range(potencial)]) + ''.join([f'<span class="star-gray">☆</span>' for _ in range(6 - potencial)])
                            st.markdown(f"""
                                <div class="metric-card-pro animate-fade-in">
                                    <div class="metric-value-pro">{potencial if potencial > 0 else '-'}</div>
                                    <div class="metric-label-pro">Potencial</div>
                                    <div class="stars-pro">{stars_html}</div>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # COLUMN 4: Profile (TEXT ONLY, NO STARS)
                        with col4:
                            perfil_val = report['Perfil']
                            try:
                                if isinstance(perfil_val, str) and ' - ' in perfil_val:
                                    perfil_num = int(perfil_val.split(' - ')[0])
                                    perfil_text = perfil_val.split(' - ', 1)[1] if len(perfil_val.split(' - ', 1)) > 1 else perfil_val
                                else:
                                    perfil_num = int(float(perfil_val))
                                    perfil_text = f"Level {perfil_num}"
                            except (ValueError, TypeError):
                                perfil_num = 0
                                perfil_text = "-"
                            
                            st.markdown(f"""
                                <div class="metric-card-pro animate-fade-in">
                                    <div class="metric-value-pro">{perfil_num if perfil_num > 0 else '-'}</div>
                                    <div class="metric-label-pro">Profile</div>
                                    <div class="profile-text-pro">{perfil_text}</div>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # === INFORMACIÓN SECUNDARIA ===
                        contract = report.get('Contract', 'N/A')
                        agent = report.get('Agent', 'N/A')
                        phone = report.get('Agent Phone', 'N/A')
                        report_date = report.get('Date', 'N/A')
                        scout = report.get('Scout', 'N/A')
                        
                        st.markdown(f"""
                            <div class="info-bar-pro animate-fade-in">
                                <span><strong>FIN DE CONTRATO:</strong> {contract}</span>
                                <span><strong>💼 AGENTE:</strong> {agent}</span>
                                <span><strong>📞</strong> {phone}</span>
                                <span><strong>📅</strong> {report_date}</span>
                                <span><strong>👤</strong> {scout}</span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # === SECCIÓN INFERIOR: COMENTARIO TÉCNICO Y CONCLUSIÓN (VERTICAL) ===
                        # Comentario técnico
                        tech_comment = report.get('Technical Comment', None)
                        if tech_comment and str(tech_comment) != 'nan' and str(tech_comment).strip():
                            st.markdown(f"""
                                <div class="report-box-pro animate-fade-in">
                                    <p class="report-text-pro">{tech_comment}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                                <div class="report-box-pro animate-fade-in">
                                    <p class="report-text-pro" style="color: #999;">No technical comment available.</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Conclusión (debajo del comentario)
                        conclusion = report.get('Conclusion', '')
                        
                        # Determinar clase de color según conclusión
                        if conclusion.startswith('A'):
                            button_class = ''  # Green (default)
                        elif conclusion.startswith('B+'):
                            button_class = ' blue'
                        elif conclusion.startswith('B') and not conclusion.startswith('B+'):
                            button_class = ' orange'
                        else:
                            button_class = ' blue'  # Default
                        
                        st.markdown(f"""
                            <div class="action-button-pro{button_class} animate-fade-in">
                                <p class="action-text-pro">{conclusion}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # === BOTÓN GENERAR PDF ===
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
                        with col_pdf2:
                            if st.button(f"📄 Generar PDF", key=f"pdf_{idx}", type="primary", use_container_width=True):
                                try:
                                    # Preparar datos para el PDF
                                    player_name = report['Player']
                                    
                                    # Buscar foto del jugador
                                    import os
                                    import unicodedata
                                    
                                    def remove_accents(text):
                                        """Quitar acentos de un texto"""
                                        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
                                    
                                    photo_path = None
                                    base_dir = os.path.dirname(os.path.abspath(__file__))
                                    
                                    # Versión sin acentos del nombre
                                    player_name_no_accents = remove_accents(player_name)
                                    
                                    # También reemplazar puntos por guiones bajos (G. Yassine -> G_Yassine)
                                    player_name_clean = player_name.replace('.', '_').replace(' ', '_')
                                    player_name_no_accents_clean = player_name_no_accents.replace('.', '_').replace(' ', '_')
                                    
                                    possible_photos = [
                                        # Con puntos reemplazados
                                        os.path.join(base_dir, 'player_photos', f"{player_name_clean}.png"),
                                        os.path.join(base_dir, 'player_photos', f"{player_name_no_accents_clean}.png"),
                                        # Con acentos
                                        os.path.join(base_dir, 'player_photos', f"{player_name.replace(' ', '_')}.png"),
                                        os.path.join(base_dir, 'player_photos', f"{player_name.replace(' ', '')}.png"),
                                        os.path.join(base_dir, 'player_photos', f"{player_name}.png"),
                                        # Sin acentos
                                        os.path.join(base_dir, 'player_photos', f"{player_name_no_accents.replace(' ', '_')}.png"),
                                        os.path.join(base_dir, 'player_photos', f"{player_name_no_accents.replace(' ', '')}.png"),
                                        os.path.join(base_dir, 'player_photos', f"{player_name_no_accents}.png"),
                                        # JPG
                                        os.path.join(base_dir, 'player_photos', f"{player_name_clean}.jpg"),
                                        os.path.join(base_dir, 'player_photos', f"{player_name.replace(' ', '_')}.jpg"),
                                        os.path.join(base_dir, 'player_photos', f"{player_name_no_accents.replace(' ', '_')}.jpg"),
                                    ]
                                    
                                    for path in possible_photos:
                                        if os.path.exists(path):
                                            photo_path = path
                                            st.info(f"✅ Foto encontrada: {os.path.basename(path)}")
                                            break
                                    
                                    if not photo_path:
                                        st.warning(f"⚠️ No se encontró foto para {player_name}")
                                    
                                    pdf_data = {
                                        'Player': player_name,
                                        'Team': report['Team'],
                                        'Position': report.get('Position', 'N/A'),
                                        'Birth Date': report.get('Birth Date', 'N/A'),
                                        'Performance': report.get('Rendimiento', 0),
                                        'Potential': report.get('Potencial', 0),
                                        'Profile': report.get('Perfil', 'N/A'),
                                        'Contract': report.get('Contract', 'N/A'),
                                        'Agent': report.get('Agent', 'N/A'),
                                        'Agent Phone': report.get('Agent Phone', 'N/A'),
                                        'Scout': report.get('Scout', 'N/A'),
                                        'Date': report.get('Date', datetime.now().strftime('%Y-%m-%d')),
                                        'Technical Comment': report.get('Technical Comment', 'No technical comment available.'),
                                        'Conclusion': report.get('Conclusion', 'B - Seguir'),
                                        'photo_path': photo_path  # Ruta absoluta a la foto
                                    }
                                    
                                    # Generar PDF directamente en memoria (compatible con Render/Cloud)
                                    pdf_bytes = generate_individual_report_pdf(pdf_data, return_bytes=True)
                                    
                                    # Generar nombre del archivo
                                    player_name_safe = pdf_data['Player'].replace(' ', '_').replace('.', '')
                                    pdf_filename = f"{player_name_safe}_IndividualReport_{pdf_data['Date']}.pdf"
                                    
                                    st.success("✅ PDF generado correctamente!")
                                    
                                    # Botón de descarga
                                    st.download_button(
                                        label="⬇️ Descargar PDF",
                                        data=pdf_bytes,
                                        file_name=pdf_filename,
                                        mime="application/pdf"
                                    )
                                    
                                except Exception as e:
                                    st.error(f"❌ Error al generar PDF: {str(e)}")
                                    import traceback
                                    st.code(traceback.format_exc())
            else:
                st.info("🔍 No individual reports found. Create one in the CREATE INDIVIDUAL REPORT tab.")
        
        except FileNotFoundError:
            st.info("📊 No individual reports yet. Create your first report!")
        except Exception as e:
            st.error(f"Error loading reports: {e}")
    
    # Tab 4: DATABASE (content from old tab 3)
    with tabs[4]:
        # Load Al Nassr logo for title
        try:
            from PIL import Image
            import io
            logo_title = Image.open('alnassr.png')
            logo_title.thumbnail((30, 30))
            buffered_title = io.BytesIO()
            if logo_title.mode in ('RGBA', 'LA', 'P'):
                logo_title.save(buffered_title, format="PNG")
            else:
                logo_title = logo_title.convert('RGB')
                logo_title.save(buffered_title, format="PNG")
            logo_title_str = base64.b64encode(buffered_title.getvalue()).decode()
            logo_title_html = f'<img src="data:image/png;base64,{logo_title_str}" style="height:24px; vertical-align:middle; margin-right:8px;">'
        except:
            logo_title_html = '🗄️'
        
        if st.session_state.language == 'en':
            st.markdown(f"<h3>{logo_title_html} Player Database - FIFA U17 World Cup</h3>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h3>{logo_title_html} قاعدة بيانات اللاعبين - كأس العالم تحت 17</h3>", unsafe_allow_html=True)
        
        # Custom CSS for player cards
        st.markdown("""
        <style>
            .player-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                margin-bottom: 0.5rem;
            }
            .player-card-header {
                font-size: 1.2rem;
                font-weight: bold;
            }
            .player-badge {
                display: inline-block;
                background-color: rgba(255,255,255,0.2);
                padding: 0.3rem 0.6rem;
                border-radius: 15px;
                margin-right: 0.5rem;
                font-size: 0.9rem;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Load player data from Google Sheets (WorldCupU17Data)
        # Columns: # POS PLAYER NAME ... Team CLUB Nationality
        df_players = pd.DataFrame()
        team_col = 'Team'  # Selección nacional (para agrupar)
        club_col = 'CLUB'  # Club de origen (solo informativo)
        position_col = 'POS'
        name_col = 'PLAYER NAME'
        
        try:
            # Try Google Sheets first
            df_players = read_google_sheet('WorldCupU17Data', 'Sheet1')
            
            # If Google Sheets fails, try local Excel file
            if df_players is None or df_players.empty:
                try:
                    df_players = pd.read_excel('dbworldcup17.xlsx')
                    if not df_players.empty:
                        st.info(f"📊 {len(df_players)} jugadores cargados")
                except Exception as excel_error:
                    st.error(f"❌ Error al cargar datos: {str(excel_error)}")
                    df_players = pd.DataFrame()
            else:
                st.info(f"📊 {len(df_players)} jugadores cargados")
            
            # Verificar columnas
            if not df_players.empty:
                if 'Team' in df_players.columns:
                    team_col = 'Team'
                if 'CLUB' in df_players.columns:
                    club_col = 'CLUB'
                if 'POS' in df_players.columns:
                    position_col = 'POS'
                if 'PLAYER NAME' in df_players.columns:
                    name_col = 'PLAYER NAME'
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            
        # Load match reports from Google Sheets
        try:
            df_reports = read_google_sheet('fifa_u17_match_reports', 'Sheet1')
        except FileNotFoundError:
            df_reports = pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading reports: {e}")
        
        # Try to load individual reports (silently fail if empty)
        try:
            df_individual_reports = read_google_sheet('fifa_u17_individual_reports', 'Sheet1')
            if df_individual_reports is None:
                df_individual_reports = pd.DataFrame()
        except:
            df_individual_reports = pd.DataFrame()
        
        # Control para mostrar todos los jugadores
        if 'show_all_players' not in st.session_state:
            st.session_state.show_all_players = False
        
        # Botón para mostrar todos
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            if st.button("👥 Mostrar todos" if not st.session_state.show_all_players else "❌ Ocultar", key="toggle_show_all_players"):
                st.session_state.show_all_players = not st.session_state.show_all_players
                st.rerun()
        
        # Filters
        st.markdown("---")
        st.markdown("### 🔍 Filtros / Filters")
        col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
        
        with col_filter1:
            # Search by player name
            search_player = st.text_input(
                "🔍 Search Player" if st.session_state.language == 'en' else "🔍 ابحث عن لاعب",
                placeholder="Enter player name..." if st.session_state.language == 'en' else "أدخل اسم اللاعب...",
                key="fifa_u17_search_player"
            )
        
        # Use all players for filters
        base_df_for_filters_db = df_players
        
        with col_filter2:
            # Position filter
            if not base_df_for_filters_db.empty and position_col in base_df_for_filters_db.columns:
                all_positions = ['All Positions'] + sorted(base_df_for_filters_db[position_col].dropna().unique().tolist())
            else:
                all_positions = ['All Positions']
            selected_position = st.selectbox(
                "⚽ Position" if st.session_state.language == 'en' else "⚽ المركز",
                all_positions,
                key="fifa_u17_position_filter"
            )
        
        with col_filter3:
            # Team filter (Team column - national teams)
            if not base_df_for_filters_db.empty and team_col in base_df_for_filters_db.columns:
                all_teams = ['All Teams'] + sorted(base_df_for_filters_db[team_col].unique().tolist())
            else:
                all_teams = ['All Teams']
            selected_team = st.selectbox(
                "🌍 Team" if st.session_state.language == 'en' else "🌍 الفريق",
                all_teams,
                key="fifa_u17_team_filter"
            )
        
        with col_filter4:
            # Conclusion filter
            conclusion_options = ['Todas', 'A - Firmar', 'B+ - Seguir para Firmar', 'B - Seguir']
            selected_conclusion = st.selectbox(
                "🎯 Conclusión",
                conclusion_options,
                key="fifa_u17_conclusion_filter"
            )
        
        # Checkbox para mostrar solo jugadores con informe
        col_check1, col_check2 = st.columns([2, 4])
        with col_check1:
            only_with_reports = st.checkbox(
                "📊 Mostrar solo jugadores con informe",
                value=False,
                key="only_with_reports_filter"
            )
        
        # Filter dataframe
        filtered_df = df_players.copy()
        
        if selected_team != 'All Teams':
            filtered_df = filtered_df[filtered_df[team_col] == selected_team]
        
        if selected_position != 'All Positions':
            filtered_df = filtered_df[filtered_df[position_col] == selected_position]
        
        if search_player:
            filtered_df = filtered_df[filtered_df[name_col].str.contains(search_player, case=False, na=False)]
        
        # Filtrar por jugadores con informe
        if only_with_reports:
            players_with_any_report = []
            
            # Añadir jugadores con match reports
            if not df_reports.empty:
                players_with_any_report.extend(df_reports['Player Name'].unique().tolist())
            
            # Añadir jugadores con individual reports
            if not df_individual_reports.empty:
                players_with_any_report.extend(df_individual_reports['Player'].unique().tolist())
            
            # Filtrar solo jugadores con informe
            if players_with_any_report:
                filtered_df = filtered_df[filtered_df[name_col].isin(players_with_any_report)]
            else:
                filtered_df = pd.DataFrame()  # No hay jugadores con informe
        
        # Filtrar por conclusión
        if selected_conclusion != 'Todas':
            players_with_conclusion = []
            
            # Buscar en match reports
            if not df_reports.empty and 'Conclusion' in df_reports.columns:
                if selected_conclusion == 'A - Firmar':
                    # Buscar A al inicio de la conclusión
                    conclusion_reports = df_reports[df_reports['Conclusion'].astype(str).str.strip().str.upper().str.match(r'^A[\s\-]')]
                elif selected_conclusion == 'B+ - Seguir para Firmar':
                    # Buscar específicamente B+
                    conclusion_reports = df_reports[df_reports['Conclusion'].astype(str).str.contains(r'B\+', case=False, na=False, regex=True)]
                elif selected_conclusion == 'B - Seguir':
                    # Buscar B pero NO B+
                    conclusion_reports = df_reports[
                        (df_reports['Conclusion'].astype(str).str.strip().str.upper().str.match(r'^B[\s\-]')) &
                        (~df_reports['Conclusion'].astype(str).str.contains(r'B\+', case=False, na=False, regex=True))
                    ]
                else:
                    conclusion_reports = pd.DataFrame()
                
                if not conclusion_reports.empty:
                    players_with_conclusion.extend(conclusion_reports['Player Name'].unique().tolist())
            
            # Buscar en individual reports
            if not df_individual_reports.empty and 'Conclusion' in df_individual_reports.columns:
                if selected_conclusion == 'A - Firmar':
                    # Buscar A al inicio de la conclusión
                    conclusion_ind_reports = df_individual_reports[df_individual_reports['Conclusion'].astype(str).str.strip().str.upper().str.match(r'^A[\s\-]')]
                elif selected_conclusion == 'B+ - Seguir para Firmar':
                    # Buscar específicamente B+
                    conclusion_ind_reports = df_individual_reports[df_individual_reports['Conclusion'].astype(str).str.contains(r'B\+', case=False, na=False, regex=True)]
                elif selected_conclusion == 'B - Seguir':
                    # Buscar B pero NO B+
                    conclusion_ind_reports = df_individual_reports[
                        (df_individual_reports['Conclusion'].astype(str).str.strip().str.upper().str.match(r'^B[\s\-]')) &
                        (~df_individual_reports['Conclusion'].astype(str).str.contains(r'B\+', case=False, na=False, regex=True))
                    ]
                else:
                    conclusion_ind_reports = pd.DataFrame()
                
                if not conclusion_ind_reports.empty:
                    players_with_conclusion.extend(conclusion_ind_reports['Player'].unique().tolist())
            
            # Filtrar solo jugadores con esa conclusión
            if players_with_conclusion:
                filtered_df = filtered_df[filtered_df[name_col].isin(players_with_conclusion)]
            else:
                filtered_df = pd.DataFrame()  # No hay jugadores con esa conclusión
        
        # Si no se ha activado "Mostrar todos" y no hay filtros activos, no mostrar nada
        has_active_filters = (
            search_player or 
            selected_position != 'All Positions' or 
            selected_team != 'All Teams' or
            only_with_reports or
            selected_conclusion != 'Todas'
        )
        
        if not st.session_state.show_all_players and not has_active_filters:
            filtered_df = pd.DataFrame()  # No mostrar nada
        
        st.markdown("---")
        
        # Display stats
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("👥 Total Players", len(filtered_df))
        with col_stat2:
            st.metric("🌍 Teams", filtered_df[team_col].nunique() if not filtered_df.empty else 0)
        with col_stat3:
            # Count players with match reports
            if not df_reports.empty and not filtered_df.empty:
                players_with_match_reports = filtered_df[name_col].isin(df_reports['Player Name']).sum()
                st.metric("⚽ Match Reports", players_with_match_reports)
            else:
                st.metric("⚽ Match Reports", 0)
        with col_stat4:
            # Count players with individual reports
            if not df_individual_reports.empty and not filtered_df.empty:
                players_with_individual_reports = filtered_df[name_col].isin(df_individual_reports['Player']).sum()
                st.metric("📋 Individual Reports", players_with_individual_reports)
            else:
                st.metric("📋 Individual Reports", 0)
        
        st.markdown("---")
        
        # Download buttons for Player Database
        if not filtered_df.empty:
            st.markdown("### 📥 Descargar Datos / Download Data")
            create_download_buttons(
                filtered_df, 
                filename_base="fifa_u17_player_database",
                label_prefix="Descargar / Download"
            )
            st.markdown("---")
        
        if filtered_df.empty:
            if not st.session_state.show_all_players and not has_active_filters:
                st.info("👥 Haz clic en 'Mostrar todos' o usa los filtros para ver los jugadores" if st.session_state.language == 'en' else "👥 انقر على 'إظهار الكل' أو استخدم الفلاتر لمشاهدة اللاعبين")
            else:
                st.warning("❌ No se encontraron jugadores con los filtros seleccionados" if st.session_state.language == 'en' else "❌ لا يوجد لاعبون بالفلاتر المحددة")
        else:
            # Group by team (Team column - national teams)
            for team in sorted(filtered_df[team_col].unique()):
                team_players = filtered_df[filtered_df[team_col] == team]
                
                # Team header with flag emoji
                flag_emoji = COUNTRY_FLAG_EMOJI.get(team, '🏴')
                flag_html = f'<span style="font-size:40px; margin-right:10px;">{flag_emoji}</span>'
                
                # Count players with match reports in this team
                team_players_with_match_reports = 0
                if not df_reports.empty:
                    team_players_with_match_reports = team_players[name_col].isin(df_reports['Player Name']).sum()
                
                # Count players with individual reports in this team
                team_players_with_individual_reports = 0
                if not df_individual_reports.empty:
                    team_players_with_individual_reports = team_players[name_col].isin(df_individual_reports['Player']).sum()
                
                # Display team header
                st.markdown(
                    f'<div style="background-color: #002B5B; color: white; padding: 1rem; border-radius: 8px; margin: 1rem 0; font-weight: bold; font-size: 1.2rem;">{flag_html}{team} ({len(team_players)} players | ⚽ {team_players_with_match_reports} match reports | 📋 {team_players_with_individual_reports} individual reports)</div>',
                    unsafe_allow_html=True
                )
                
                # Display players as expandable cards within this team
                for idx, player in team_players.iterrows():
                    player_name = player[name_col]
                    player_position = player.get(position_col, 'N/A')
                    player_team = player[team_col]  # Selección nacional
                    player_club = player.get(club_col, 'N/A')  # Club de origen (informativo)
                    player_age = player.get('DOB', 'N/A')  # Fecha de nacimiento
                    
                    # Check if player has match reports
                    has_match_reports = False
                    player_reports = pd.DataFrame()
                    if not df_reports.empty:
                        player_reports = df_reports[df_reports['Player Name'] == player_name]
                        has_match_reports = len(player_reports) > 0
                    
                    # Check if player has individual reports
                    has_individual_reports = False
                    player_individual_reports = pd.DataFrame()
                    if not df_individual_reports.empty:
                        # Try exact match first
                        player_individual_reports = df_individual_reports[df_individual_reports['Player'] == player_name]
                        # If no exact match, try case-insensitive and stripped
                        if len(player_individual_reports) == 0:
                            player_individual_reports = df_individual_reports[
                                df_individual_reports['Player'].str.strip().str.lower() == player_name.strip().lower()
                            ]
                        has_individual_reports = len(player_individual_reports) > 0
                    
                    # Card header with status indicator
                    has_any_report = has_match_reports or has_individual_reports
                    
                    # Determinar emoji según conclusión - revisar TODOS los informes
                    status_emoji = ""
                    best_conclusion_priority = 0  # 0=ninguno, 1=otros, 2=B, 3=B+, 4=A
                    
                    if has_any_report:
                        # Revisar individual reports
                        if has_individual_reports:
                            for _, ind_report in player_individual_reports.iterrows():
                                conclusion = str(ind_report.get('Conclusion', '')).strip()
                                conclusion_upper = conclusion.upper()
                                
                                # Determinar prioridad
                                if conclusion_upper.startswith('A ') or conclusion_upper.startswith('A-') or (conclusion_upper.startswith('A') and len(conclusion_upper) > 1 and conclusion_upper[1] in [' ', '-']):
                                    if best_conclusion_priority < 4:
                                        best_conclusion_priority = 4
                                        status_emoji = "⭐️"
                                elif 'B+' in conclusion_upper or 'B +' in conclusion_upper:
                                    if best_conclusion_priority < 3:
                                        best_conclusion_priority = 3
                                        status_emoji = "🟢"
                                elif conclusion_upper.startswith('B ') or conclusion_upper.startswith('B-'):
                                    if best_conclusion_priority < 2:
                                        best_conclusion_priority = 2
                                        status_emoji = "☑️"
                                elif conclusion and conclusion != 'nan':
                                    if best_conclusion_priority < 1:
                                        best_conclusion_priority = 1
                                        status_emoji = "☑️"
                        
                        # Revisar match reports
                        if has_match_reports:
                            for _, match_report in player_reports.iterrows():
                                match_conclusion = str(match_report.get('Conclusion', '')).strip()
                                match_conclusion_upper = match_conclusion.upper()
                                
                                # Determinar prioridad
                                if match_conclusion_upper.startswith('A ') or match_conclusion_upper.startswith('A-') or (match_conclusion_upper.startswith('A') and len(match_conclusion_upper) > 1 and match_conclusion_upper[1] in [' ', '-']):
                                    if best_conclusion_priority < 4:
                                        best_conclusion_priority = 4
                                        status_emoji = "⭐️"
                                elif 'B+' in match_conclusion_upper or 'B +' in match_conclusion_upper:
                                    if best_conclusion_priority < 3:
                                        best_conclusion_priority = 3
                                        status_emoji = "🟢"
                                elif match_conclusion_upper.startswith('B ') or match_conclusion_upper.startswith('B-'):
                                    if best_conclusion_priority < 2:
                                        best_conclusion_priority = 2
                                        status_emoji = "☑️"
                                elif match_conclusion and match_conclusion != 'nan':
                                    if best_conclusion_priority < 1:
                                        best_conclusion_priority = 1
                                        status_emoji = "☑️"
                        
                        # Si no se encontró ninguna conclusión válida
                        if not status_emoji:
                            status_emoji = "☑️"
                    
                    # Siempre usar fondo blanco (sin color)
                    card_bg_color = "white"
                    
                    # Al Nassr minimalist player profile
                    with st.container():
                        # Get player photo
                        player_photo_base64 = ""
                        try:
                            from PIL import Image
                            import io
                            import os
                            
                            player_photo_file = f"player_photos/{player_name.replace(' ', '_')}.jpg"
                            if not os.path.exists(player_photo_file):
                                player_photo_file = 'profile1.jpg'
                            
                            if os.path.exists(player_photo_file):
                                img = Image.open(player_photo_file)
                                img.thumbnail((120, 120), Image.Resampling.LANCZOS)
                                buffered = io.BytesIO()
                                
                                if img.mode in ('RGBA', 'LA', 'P'):
                                    img.save(buffered, format="PNG")
                                else:
                                    img = img.convert('RGB')
                                    img.save(buffered, format="PNG")
                                
                                player_photo_base64 = base64.b64encode(buffered.getvalue()).decode()
                        except:
                            pass
                        
                        # Birth year
                        birth_year = str(player.get('Año', ''))[:4] if player.get('Año') else 'N/A'
                        contract_date = str(player.get('Fin Contrato', 'N/A'))[:10]
                        
                        # Expander con el nombre del jugador
                        with st.expander(
                            f"{status_emoji} **{player_name}**",
                            expanded=False
                        ):
                            # Al Nassr Header Section
                            photo_html = f'<img src="data:image/png;base64,{player_photo_base64}" style="width:120px; height:120px; border-radius:50%; object-fit:cover; border:3px solid #FFC60A;">' if player_photo_base64 else '<div style="width:120px; height:120px; border-radius:50%; background:#FFC60A; display:flex; align-items:center; justify-content:center; font-size:48px; border:3px solid #FFC60A;">👤</div>'
                            
                            st.markdown(f"""
                                <div style="background: #1a2332; padding: 30px; border-radius: 8px; margin-bottom: 30px;">
                                    <div style="display: flex; align-items: center; gap: 30px; flex-wrap: wrap;">
                                        <div>{photo_html}</div>
                                        <div style="flex: 1; min-width: 300px;">
                                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px;">
                                                <div>
                                                    <div style="color: #FFC60A; font-size: 12px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px;">POSITION</div>
                                                    <div style="color: white; font-size: 24px; font-weight: 600;">{player_position}</div>
                                                </div>
                                                <div>
                                                    <div style="color: #FFC60A; font-size: 12px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px;">NATIONAL TEAM</div>
                                                    <div style="color: white; font-size: 20px; font-weight: 600;">{player_team}</div>
                                                </div>
                                                <div>
                                                    <div style="color: #FFC60A; font-size: 12px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px;">CLUB</div>
                                                    <div style="color: white; font-size: 16px; font-weight: 500;">{player_club}</div>
                                                </div>
                                                <div>
                                                    <div style="color: #FFC60A; font-size: 12px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px;">DOB</div>
                                                    <div style="color: white; font-size: 18px; font-weight: 600;">{player_age}</div>
                                                </div>
                                                <div>
                                                    <div style="color: #FFC60A; font-size: 12px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px;">YEAR</div>
                                                    <div style="color: white; font-size: 24px; font-weight: 600;">{birth_year}</div>
                                                </div>
                                                <div>
                                                    <div style="color: #FFC60A; font-size: 12px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px;">CONTRACT</div>
                                                    <div style="color: white; font-size: 24px; font-weight: 600;">{contract_date}</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Photo upload section
                            st.markdown("---")
                            col_upload1, col_upload2 = st.columns([2, 4])
                            
                            with col_upload1:
                                uploaded_player_photo = st.file_uploader(
                                    "📷 Subir Foto del Jugador",
                                    type=['jpg', 'jpeg', 'png'],
                                    key=f"upload_photo_{idx}_{player_name.replace(' ', '_').replace('.', '_')}",
                                    help="Sube una foto del jugador"
                                )
                                
                                if uploaded_player_photo:
                                    if st.button("💾 Guardar Foto", key=f"save_photo_{idx}_{player_name.replace(' ', '_').replace('.', '_')}"):
                                        import os
                                        os.makedirs('player_photos', exist_ok=True)
                                        photo_filename = f"player_photos/{player_name.replace(' ', '_')}.jpg"
                                        with open(photo_filename, 'wb') as f:
                                            f.write(uploaded_player_photo.getbuffer())
                                        st.success("✅ Foto guardada correctamente!")
                                        time.sleep(1)
                                        st.rerun()
                            
                            st.markdown("---")
                            
                            # Match Reports Section with Al Nassr Design
                            if has_match_reports:
                                st.markdown(f"""
                                    <div style="color: #1a2332; font-size: 20px; font-weight: 700; margin: 20px 0 15px 0;">
                                        {len(player_reports)} Match Report(s)
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Display each match report card
                                for rep_idx, report in player_reports.iterrows():
                                    match_date = report['Date']
                                    match_teams = report['Match']
                                    scout = report['Scout']
                                    phase = report['Phase']
                                    performance = report['Performance']
                                    potential = report['Potential']
                                    conclusion = report.get('Conclusion', 'B - Seguir')
                                    full_report = report.get('Report', '')
                                    
                                    # Conclusion badge color
                                    conclusion_str = str(conclusion).strip().upper()
                                    if 'A -' in conclusion_str or 'A-' in conclusion_str or conclusion_str.startswith('A '):
                                        conclusion_color = '#4CAF50'  # Green for A
                                        conclusion_bg = 'rgba(76, 175, 80, 0.1)'
                                    elif 'B+' in conclusion_str:
                                        conclusion_color = '#4CAF50'  # Green for B+
                                        conclusion_bg = 'rgba(76, 175, 80, 0.1)'
                                    else:
                                        conclusion_color = '#ff8c00'  # Orange for B
                                        conclusion_bg = 'rgba(255, 140, 0, 0.1)'
                                    
                                    # Performance percentage for red gradient bar
                                    perf_percent = (performance / 6) * 100
                                    pot_percent = (potential / 6) * 100
                                    
                                    # Unique key for toggle
                                    toggle_key = f"toggle_report_{idx}_{player_name.replace(' ', '_').replace('.', '_')}_{rep_idx}"
                                    if toggle_key not in st.session_state:
                                        st.session_state[toggle_key] = False
                                    
                                    # Match Report Card with Al Nassr Design
                                    st.markdown(f'''
                                    <div style="border: 2px solid #e0e0e0; border-radius: 8px; margin-bottom: 15px; overflow: hidden;">
                                        <div style="background: #1a2332; padding: 15px 20px; color: white;">
                                            <div style="font-size: 16px; font-weight: 600;">{match_date} | {match_teams}</div>
                                        </div>
                                        <div style="background: #f9f9f9; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                                            <div style="font-size: 13px; color: #666;">
                                                <strong>Scout:</strong> {scout} | <strong>Phase:</strong> {phase}
                                            </div>
                                            <div style="background: {conclusion_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase;">
                                                {conclusion}
                                            </div>
                                        </div>
                                        <div style="padding: 20px; background: white;">
                                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                                <div>
                                                    <div style="font-size: 12px; color: #666; margin-bottom: 8px; font-weight: 600;">PERFORMANCE</div>
                                                    <div style="font-size: 24px; font-weight: 700; color: #1a2332; margin-bottom: 8px;">{performance}/6</div>
                                                    <div style="background: #f0f0f0; border-radius: 10px; height: 8px; overflow: hidden;">
                                                        <div style="background: linear-gradient(90deg, #ff4444, #ff6666); height: 100%; width: {perf_percent}%; border-radius: 10px;"></div>
                                                    </div>
                                                </div>
                                                <div>
                                                    <div style="font-size: 12px; color: #666; margin-bottom: 8px; font-weight: 600;">POTENTIAL</div>
                                                    <div style="font-size: 24px; font-weight: 700; color: #1a2332; margin-bottom: 8px;">{potential}/6</div>
                                                    <div style="background: #f0f0f0; border-radius: 10px; height: 8px; overflow: hidden;">
                                                        <div style="background: linear-gradient(90deg, #ff4444, #ff6666); height: 100%; width: {pot_percent}%; border-radius: 10px;"></div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    ''', unsafe_allow_html=True)
                                    
                                    # Toggle button for full report
                                    if full_report and str(full_report).strip() and str(full_report) != 'nan':
                                        col_btn, col_space = st.columns([1, 5])
                                        with col_btn:
                                            button_text = "▼ Ver Reporte" if not st.session_state[toggle_key] else "▲ Ocultar"
                                            if st.button(button_text, key=f"btn_{toggle_key}"):
                                                st.session_state[toggle_key] = not st.session_state[toggle_key]
                                                st.rerun()
                                        
                                        # Show report if toggled
                                        if st.session_state[toggle_key]:
                                            st.markdown(f"""
                                                <div style="border-top: 3px solid #FFC60A; padding: 20px; background: #f5f5f5; margin-top: -15px; margin-bottom: 15px; border-radius: 0 0 8px 8px;">
                                                    <div style="color: #333; line-height: 1.6;">{full_report}</div>
                                                </div>
                                            """, unsafe_allow_html=True)
                            
                            # Individual Report Section (if exists)
                            if has_individual_reports:
                                st.markdown("""
                                    <div style="color: #1a2332; font-size: 20px; font-weight: 700; margin: 30px 0 15px 0;">
                                        Individual Reports
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Calcular medias
                                num_reports = len(player_individual_reports)
                                avg_rendimiento = player_individual_reports['Rendimiento'].mean()
                                avg_potencial = player_individual_reports['Potencial'].mean()
                                
                                # Obtener lista de scouts
                                scouts_list = player_individual_reports['Scout'].dropna().unique().tolist()
                                scouts_text = ", ".join(scouts_list) if scouts_list else "N/A"
                                
                                # Mostrar información general
                                st.markdown(f"📊 **{num_reports} Informe(s) de: {scouts_text}**")
                                st.markdown("")
                                
                                # Cargar logo Al Nassr para las tarjetas
                                try:
                                    from PIL import Image
                                    import io
                                    logo_img = Image.open('alnassr.png')
                                    logo_img.thumbnail((40, 40))
                                    buffered = io.BytesIO()
                                    if logo_img.mode in ('RGBA', 'LA', 'P'):
                                        logo_img.save(buffered, format="PNG")
                                    else:
                                        logo_img = logo_img.convert('RGB')
                                        logo_img.save(buffered, format="PNG")
                                    logo_str = base64.b64encode(buffered.getvalue()).decode()
                                    logo_html = f'<img src="data:image/png;base64,{logo_str}" style="height:24px; margin-bottom:8px;">'
                                except:
                                    logo_html = '<div style="font-size:24px; margin-bottom:10px;">🦅</div>'
                                
                                # Mostrar valoraciones medias en 2 columnas con estilo minimalista
                                col_avg1, col_avg2 = st.columns(2)
                                
                                with col_avg1:
                                    st.markdown("""
                                        <div style="background: white; padding: 20px 18px; border-radius: 10px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1.5px solid #FFD700;">
                                            {}
                                            <p style="font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; font-weight: 600;">🎯 RENDIMIENTO</p>
                                            <h1 style="font-size: 48px; font-weight: 700; color: #1B2845; margin: 8px 0; line-height: 1;">{:.1f}</h1>
                                            <p style="font-size: 10px; color: #999; margin-top: 6px;">Sobre 6.0</p>
                                        </div>
                                    """.format(logo_html, avg_rendimiento), unsafe_allow_html=True)
                                
                                with col_avg2:
                                    st.markdown("""
                                        <div style="background: white; padding: 20px 18px; border-radius: 10px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1.5px solid #FFD700;">
                                            {}
                                            <p style="font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; font-weight: 600;">⭐ POTENCIAL</p>
                                            <h1 style="font-size: 48px; font-weight: 700; color: #1B2845; margin: 8px 0; line-height: 1;">{:.1f}</h1>
                                            <p style="font-size: 10px; color: #999; margin-top: 6px;">Sobre 6.0</p>
                                        </div>
                                    """.format(logo_html, avg_potencial), unsafe_allow_html=True)
                                
                                # Si solo hay 1 informe, mostrar nota
                                st.markdown("")
                                if num_reports == 1:
                                    st.info("ℹ️ Este jugador tiene 1 informe individual.")
                                else:
                                    st.success(f"✅ Media calculada de {num_reports} informes de diferentes scouts.")
                                
                                # Mostrar informes individuales
                                st.markdown("---")
                                st.markdown(f"### 📝 Informes Individuales ({num_reports})")
                                st.markdown("")
                                
                                for idx, ind_report in player_individual_reports.iterrows():
                                    scout_name = ind_report.get('Scout', 'Sin nombre')
                                    if pd.isna(scout_name) or str(scout_name).strip() == '' or str(scout_name) == 'nan':
                                        scout_name = "Sin nombre"
                                    
                                    report_date = ind_report.get('Date', 'N/A')
                                    
                                    with st.expander(f"👤 {scout_name} - 📅 {report_date}", expanded=False):
                                        col_r1, col_r2 = st.columns(2)
                                        
                                        with col_r1:
                                            st.metric("🎯 Rendimiento", f"{ind_report['Rendimiento']}/6")
                                        
                                        with col_r2:
                                            st.metric("⭐ Potencial", f"{ind_report['Potencial']}/6")
                                        
                                        # Perfil
                                        perfil_val = ind_report.get('Perfil', 'N/A')
                                        if isinstance(perfil_val, str) and '-' in perfil_val:
                                            st.markdown(f"🏆 **Perfil:** {perfil_val}")
                                        else:
                                            st.markdown(f"🏆 **Perfil:** {perfil_val}/6")
                                        
                                        # Technical comment
                                        tech_comment = ind_report.get('Technical Comment', None)
                                        if tech_comment and str(tech_comment) != 'nan' and str(tech_comment).strip():
                                            st.markdown("💬 **Comentario Técnico:**")
                                            st.info(tech_comment)
                                        
                                        # Conclusion
                                        conclusion_text = ind_report.get('Conclusion', '')
                                        if conclusion_text and str(conclusion_text) != 'nan':
                                            st.markdown(f"✅ **Conclusión:** {conclusion_text}")
                            
                            # Player card display complete
    
    # Tab 2: VIEW MATCH REPORTS (content from old tab 4)
    with tabs[2]:
        # Al Nassr Match Reports CSS
        st.markdown("""
            <style>
            .stats-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
                border-left: 4px solid #FFC60A;
            }
            .stats-number {
                font-size: 36px;
                font-weight: 700;
                color: #1a2332;
                margin: 10px 0;
            }
            .stats-label {
                font-size: 12px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 600;
            }
            .match-card {
                background: white;
                border-left: 4px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 15px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .match-card:hover {
                border-left-color: #FFC60A;
                transform: translateX(5px);
                box-shadow: 0 4px 12px rgba(255,198,10,0.3);
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Title with Al Nassr logo
        try:
            from PIL import Image
            import io
            logo_dashboard = Image.open('alnassr.png')
            logo_dashboard.thumbnail((40, 40))
            buffered_logo = io.BytesIO()
            if logo_dashboard.mode in ('RGBA', 'LA', 'P'):
                logo_dashboard.save(buffered_logo, format="PNG")
            else:
                logo_dashboard = logo_dashboard.convert('RGB')
                logo_dashboard.save(buffered_logo, format="PNG")
            logo_dashboard_str = base64.b64encode(buffered_logo.getvalue()).decode()
            logo_dashboard_html = f'<img src="data:image/png;base64,{logo_dashboard_str}" style="height:32px; vertical-align:middle; margin-right:10px;">'
        except:
            logo_dashboard_html = '⚽'
        
        st.markdown(f"<h2 style='text-align: center; color: #1a2332;'>{logo_dashboard_html} MATCH REPORTS DASHBOARD</h2>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #666;'>FIFA U17 World Cup</h3>", unsafe_allow_html=True)
        
        # Botón de recarga
        col_reload, col_space = st.columns([1, 5])
        with col_reload:
            if st.button("🔄 Recargar", key="reload_match_reports"):
                st.rerun()
        
        # Scout photo name mapping
        SCOUT_PHOTO_MAP = {
            'Alvaro Lopez': 'alvaro',
            'Alvaro': 'alvaro',
            'Álvaro': 'alvaro',
            'Álvaro Lopez': 'alvaro',
            'Juan Gambero': 'juan',
            'Juan': 'juan',
            'Rafa Gil': 'rafa',
            'Rafa': 'rafa',
            'Rafael Gil': 'rafa'
        }
        
        # Country flag mapping - Complete
        COUNTRY_FLAG_MAP = {
            'Arabia Saudita': 'saff.png',
            'Italia': 'italia.png',
            'Estados Unidos': 'usa.png',
            'Francia': 'francia.png',
            'Argentina': 'afa.png',
            'Japón': 'japan.png',
            'Japon': 'japan.png',
            'Noruega': 'noruega.png',
            'Sudáfrica': 'sudafrica.png',
            'Sudafrica': 'sudafrica.png',
            'Nueva Caledonia': 'nuevacaledonia.png',
            'Cuba': 'cuba.png',
            'Panamá': 'panama.png',
            'Panama': 'panama.png',
            'Corea del Sur': 'korea.png',
            'Ucrania': 'ucrania.png',
            'Paraguay': 'paraguay.png',
            'Egipto': 'egipto.png',
            'Chile': 'chile.png',
            'México': 'mexico.png',
            'Mexico': 'mexico.png',
            'Marruecos': 'marruecos.png',
            'Brasil': 'brasil.png',
            'España': 'spain.png',
            'Espana': 'spain.png',
            'Nueva Zelanda': 'nuevazelanda.png',
            'Australia': 'australia.png',
            'Colombia': 'colombiau20.png',
            'Nigeria': 'nigeria.png',
            'Inglaterra': 'inglaterra.png',
            'Inglés': 'inglaterra.png',
            'Ecuador': 'ecuador.png',
            'Venezuela': 'venezuela.png',
            'Uruguay': 'uruguay.png',
            'Perú': 'peru.png',
            'Peru': 'peru.png',
            'Costa Rica': 'costarica.png',
            'Honduras': 'honduras.png',
            'Guatemala': 'guatemala.png',
            'Bolivia': 'bolivia.png'
        }
        
        # Load match reports from Google Sheets
        try:
            df_reports = read_google_sheet('fifa_u17_match_reports', 'Sheet1')
        except FileNotFoundError:
            df_reports = pd.DataFrame()
        except Exception as e:
            df_reports = pd.DataFrame()
        
        # Load player birth year data from WorldCupU17Data
        try:
            df_players_data = read_google_sheet('WorldCupU17Data', 'Sheet1')
            
            # Detect player column names in both dataframes
            player_col_reports = None
            player_col_data = None
            year_col_data = None
            
            # Check for player column in reports (could be 'Player Name', 'Player', etc.)
            for col in df_reports.columns:
                col_lower = col.lower().replace(' ', '')
                if col_lower in ['playername', 'player', 'jugador', 'nombre', 'name']:
                    player_col_reports = col
                    break
            
            # Check for player column in data (could be 'Nombre', 'Player', etc.)
            for col in df_players_data.columns:
                col_lower = col.lower().replace(' ', '')
                if col_lower in ['nombre', 'player', 'playername', 'jugador', 'name']:
                    player_col_data = col
                    break
            
            # Check for year column (could be 'Año', 'Year', 'Año')
            for col in df_players_data.columns:
                col_lower = col.lower()
                if col_lower in ['año', 'year', 'año', 'ano']:
                    year_col_data = col
                    break
            
            # Try to merge if both have player columns and year exists
            if player_col_reports and player_col_data and year_col_data:
                # Create a temporary dataframe for merge
                df_players_data_temp = df_players_data[[player_col_data, year_col_data]].copy()
                df_players_data_temp.columns = [player_col_reports, 'BirthYear']
                
                # Merge to get birth year
                df_reports = df_reports.merge(
                    df_players_data_temp,
                    on=player_col_reports,
                    how='left'
                )
        except Exception as e:
            pass  # Continue without birth year data
        
        # Detect Player column name
        player_col = None
        for col in df_reports.columns:
            col_lower = col.lower().replace(' ', '')
            if col_lower in ['playername', 'player', 'jugador', 'nombre', 'name']:
                player_col = col
                break
        
        if not player_col and len(df_reports.columns) > 0:
            # If no player column found, try to use first column or a common pattern
            for col in df_reports.columns:
                if 'player' in col.lower() or 'jugador' in col.lower() or 'nombre' in col.lower():
                    player_col = col
                    break
            if not player_col:
                st.error("⚠️ No se encontró la columna de jugadores. Columnas disponibles: " + ", ".join(df_reports.columns.tolist()))
                player_col = df_reports.columns[0]  # Use first column as fallback
        
        if df_reports.empty:
            st.info("📊 No match reports yet. Create match reports to see them here!")
        else:
            # Stats Cards at the top
            st.markdown("---")
            total_matches = df_reports['Match'].nunique()
            total_reports = len(df_reports)
            total_players = df_reports[player_col].nunique()
            total_teams = len(set([team.strip() for match in df_reports['Match'].unique() for team in str(match).split(' vs ') if ' vs ' in str(match)]))
            
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-label">⚽ Partidos</div>
                        <div class="stats-number">{total_matches}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s2:
                st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-label">📝 Reportes</div>
                        <div class="stats-number">{total_reports}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s3:
                st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-label">👥 Jugadores</div>
                        <div class="stats-number">{total_players}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s4:
                st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-label">🏆 Equipos</div>
                        <div class="stats-number">{total_teams}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Get scouts list for filtering
            scouts_in_reports = df_reports['Scout'].dropna().unique().tolist()
            
            # Filter options
            st.markdown("---")
            st.markdown("<h3 style='color: #1a2332;'>🔍 FILTROS / FILTERS</h3>", unsafe_allow_html=True)
            col_f1, col_f2, col_f3 = st.columns(3)
            
            # Use all reports for filters
            filtered_reports = df_reports.copy()
            base_df_for_filters_match = df_reports
            
            with col_f1:
                filter_scout = st.selectbox(
                    "🔍 Filter by Scout" if st.session_state.language == 'en' else "🔍 تصفية حسب الكشاف",
                    [""] + sorted(df_reports['Scout'].dropna().unique().tolist()),
                    key="filter_scout_match_reports"
                )
            
            with col_f2:
                filter_phase = st.selectbox(
                    "🏆 Filter by Phase" if st.session_state.language == 'en' else "🏆 تصفية حسب المرحلة",
                    [""] + sorted(base_df_for_filters_match['Phase'].dropna().unique().tolist()),
                    key="filter_phase_match_reports"
                )
            
            with col_f3:
                filter_conclusion = st.selectbox(
                    "✅ Filter by Conclusion" if st.session_state.language == 'en' else "✅ تصفية حسب الخلاصة",
                    ["", "A - Firmar (Sign)", "B+ - Seguir para Firmar (Follow to Sign)", "B - Seguir (Follow)"],
                    key="filter_conclusion_match_reports"
                )
            
            # Apply manual filters on top of intelligent search results
            if filter_scout:
                filtered_reports = filtered_reports[filtered_reports['Scout'] == filter_scout]
            if filter_phase:
                filtered_reports = filtered_reports[filtered_reports['Phase'] == filter_phase]
            if filter_conclusion:
                # Match exact conclusion from Excel
                filtered_reports = filtered_reports[filtered_reports['Conclusion'] == filter_conclusion]
            
            st.markdown("---")
            st.markdown(f"<p style='color: #666; font-size: 14px;'><strong>📊 Reportes filtrados:</strong> {len(filtered_reports)}</p>", unsafe_allow_html=True)
            st.markdown("")
            
            # Download buttons for Match Reports
            if not filtered_reports.empty:
                st.markdown("### 📥 Descargar Datos / Download Data")
                create_download_buttons(
                    filtered_reports, 
                    filename_base="fifa_u17_match_reports",
                    label_prefix="Descargar / Download"
                )
                st.markdown("---")
            
            # Scout name mapping for display (convert old names to full names)
            SCOUT_NAME_DISPLAY = {
                'Alvaro': 'Alvaro Lopez',
                'Álvaro': 'Alvaro Lopez',
                'Juan': 'Juan Gambero',
                'Rafa': 'Rafa Gil',
                'Rafael': 'Rafa Gil'
            }
            
            # Group by Scout first
            for scout in scouts_in_reports:
                scout_reports = filtered_reports[filtered_reports['Scout'] == scout]
                
                if len(scout_reports) == 0:
                    continue
                
                # Get display name for scout (convert short names to full names)
                scout_display_name = SCOUT_NAME_DISPLAY.get(scout, scout)
                
                # Scout Header Section with photo
                scout_filename = SCOUT_PHOTO_MAP.get(scout, None)
                if not scout_filename:
                    # Try to match partial name
                    for key in SCOUT_PHOTO_MAP.keys():
                        if key.lower() in scout.lower() or scout.lower() in key.lower():
                            scout_filename = SCOUT_PHOTO_MAP[key]
                            break
                if not scout_filename:
                    scout_filename = scout.replace(' ', '_').lower()
                
                scout_photo_path = f"{scout_filename}.png"
                scout_photo_html = ''
                try:
                    from PIL import Image
                    import io
                    import os
                    if os.path.exists(scout_photo_path):
                        scout_img = Image.open(scout_photo_path)
                        scout_img.thumbnail((50, 50))
                        buffered = io.BytesIO()
                        if scout_img.mode in ('RGBA', 'LA', 'P'):
                            scout_img.save(buffered, format="PNG")
                        else:
                            scout_img = scout_img.convert('RGB')
                            scout_img.save(buffered, format="PNG")
                        scout_img_str = base64.b64encode(buffered.getvalue()).decode()
                        scout_photo_html = f'<img src="data:image/png;base64,{scout_img_str}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 3px solid #FFC60A;">'
                    else:
                        scout_photo_html = '<div style="width: 50px; height: 50px; border-radius: 50%; background: #1a2332; display: flex; align-items: center; justify-content: center; color: #FFC60A; font-size: 24px; border: 3px solid #FFC60A;">👤</div>'
                except Exception as e:
                    scout_photo_html = '<div style="width: 50px; height: 50px; border-radius: 50%; background: #1a2332; display: flex; align-items: center; justify-content: center; color: #FFC60A; font-size: 24px; border: 3px solid #FFC60A;">👤</div>'
                
                st.markdown(f"""
                    <div style="background: #1a2332; border-left: 6px solid #FFC60A; border-radius: 8px; padding: 15px; margin: 20px 0 15px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            {scout_photo_html}
                            <div>
                                <h3 style="color: #FFC60A; margin: 0; font-size: 20px; font-weight: 700;">{scout_display_name}</h3>
                                <p style="color: white; margin: 3px 0 0 0; font-size: 11px; opacity: 0.9; letter-spacing: 1px;">SCOUT AL NASSR FC</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Group by match for this scout
                scout_matches = scout_reports['Match'].unique()
                
                for match_name in scout_matches:
                    match_reports = scout_reports[scout_reports['Match'] == match_name]
                    match_date = match_reports.iloc[0]['Date']
                    match_phase = match_reports.iloc[0]['Phase']
                    
                    # Initialize session state for this match card
                    match_key = f"match_card_{scout.replace(' ', '_')}_{match_name.replace(' ', '_')}"
                    if match_key not in st.session_state:
                        st.session_state[match_key] = False
                    
                    # Extract teams from match name
                    if ' vs ' in match_name:
                        team1, team2 = match_name.split(' vs ')
                        team1 = team1.strip()
                        team2 = team2.strip()
                    else:
                        team1 = match_name.strip()
                        team2 = ''
                    
                    # Load team flags with debug
                    # Get flag emojis for both teams
                    team1_flag_emoji = COUNTRY_FLAG_EMOJI.get(team1, '🏴')
                    team2_flag_emoji = COUNTRY_FLAG_EMOJI.get(team2, '🏴')
                    team1_flag_html = f'{team1_flag_emoji} '
                    team2_flag_html = f'{team2_flag_emoji} '
                    
                    # Match Header Card
                    match_header_html = f"""
                        <div style="background: white; border-left: 4px solid #FFC60A; border-radius: 8px; padding: 18px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                            <h4 style="color: #1a2332; margin: 0 0 8px 0; font-size: 18px; font-weight: 700;">{team1_flag_html}{team1} vs {team2_flag_html}{team2}</h4>
                            <p style="margin: 0; color: #666; font-size: 13px;">{match_date} | {match_phase}</p>
                        </div>
                    """
                    st.markdown(match_header_html, unsafe_allow_html=True)
                    
                    # Toggle button
                    if st.button(f"▼ Ver Jugadores ({len(match_reports)})" if not st.session_state[match_key] else "▲ Ocultar", key=f"btn_{match_key}"):
                        st.session_state[match_key] = not st.session_state[match_key]
                        st.rerun()
                    
                    # Show players if expanded
                    if st.session_state[match_key]:
                        # Group players by their ACTUAL team from Excel
                        teams_in_match = match_reports['Team'].unique() if 'Team' in match_reports.columns else [team1, team2]
                        
                        for team_name in teams_in_match:
                            if pd.isna(team_name) or str(team_name).strip() == '':
                                continue
                            
                            team_name = str(team_name).strip()
                            team_players = match_reports[match_reports['Team'] == team_name] if 'Team' in match_reports.columns else match_reports
                            
                            # Load team flag emoji for section header
                            team_flag_emoji = COUNTRY_FLAG_EMOJI.get(team_name, '🏴')
                            team_flag_html = f'{team_flag_emoji} '
                            
                            # Team section header
                            st.markdown(f"""
                                <div style="background: #f8f9fa; border-left: 4px solid #1a2332; padding: 12px 15px; margin: 15px 0 10px 0; border-radius: 6px;">
                                    <h5 style="margin: 0; color: #1a2332; font-size: 16px; font-weight: 700;">{team_flag_html}{team_name}</h5>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Player rows for this team
                            for p_idx, report in team_players.iterrows():
                                player_name = report[player_col]
                                performance = report['Performance']
                                potential = report['Potential']
                                full_report_text = report.get('Report', '')
                                player_position = report.get('Position', 'N/A')
                                player_number = report.get('Number', '-')
                                player_team = report.get('Team', team_name)
                                player_age = report.get('Age', 'N/A')
                                player_birth_year = report.get('BirthYear', report.get('Year', ''))
                                conclusion = report.get('Conclusion', '')
                                
                                # Determine conclusion badge color and text (order matters: B+ before B!)
                                conclusion_str = str(conclusion).strip()
                                conclusion_upper = conclusion_str.upper()
                                
                                # Check for A - FIRMAR first (exact match format from Excel)
                                if 'A - FIRMAR' in conclusion_upper or 'A -' in conclusion_str:
                                    conclusion_color = '#4CAF50'  # Green
                                    conclusion_text = 'A - FIRMAR'
                                # Check for B+ before B (MUST check B+ first! More specific)
                                elif 'B+' in conclusion_str or 'SEGUIR PARA FIRMAR' in conclusion_upper:
                                    conclusion_color = '#2196F3'  # Blue
                                    conclusion_text = 'B+ - SEGUIR PARA FIRMAR'
                                # Then check for B - SEGUIR (but not B+)
                                elif 'B - SEGUIR' in conclusion_upper and 'B+' not in conclusion_str:
                                    conclusion_color = '#FF9800'  # Orange
                                    conclusion_text = 'B - SEGUIR'
                                elif 'B -' in conclusion_str and '+' not in conclusion_str:
                                    conclusion_color = '#FF9800'  # Orange
                                    conclusion_text = 'B - SEGUIR'
                                else:
                                    conclusion_color = '#9E9E9E'  # Gray for unknown
                                    conclusion_text = conclusion_str if conclusion_str and conclusion_str != 'nan' else 'N/A'
                                
                                # Load player's team flag emoji
                                flag_emoji = COUNTRY_FLAG_EMOJI.get(str(player_team).strip(), '🏴')
                                flag_html = f'<span style="font-size: 18px; margin-right: 6px;">{flag_emoji}</span>'
                                
                                # Progress bars (RED)
                                perf_percent = (performance / 6) * 100
                                pot_percent = (potential / 6) * 100
                                
                                # Unique key for expand/collapse
                                player_key = f"player_report_{scout.replace(' ', '_')}_{match_name.replace(' ', '_')}_{p_idx}"
                                if player_key not in st.session_state:
                                    st.session_state[player_key] = False
                                
                                # Build birth year display
                                if player_birth_year and str(player_birth_year) not in ['nan', '', 'None']:
                                    try:
                                        birth_year_int = int(float(player_birth_year))
                                        birth_year_display = f"{birth_year_int} • "
                                    except:
                                        birth_year_display = f"{player_birth_year} • "
                                else:
                                    birth_year_display = ""
                                
                                # Horizontal player card: Nombre • Year • Posición | Rendimiento | Potencial | Conclusion Badge
                                player_card_html = f"""
                                    <div style="background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                                        <div style="flex: 1; min-width: 200px;">
                                            <div style="font-size: 15px; font-weight: 700; color: #1a2332; margin-bottom: 2px;">{player_name}</div>
                                            <div style="font-size: 11px; color: #999;">{birth_year_display}{player_position} • {player_number}</div>
                                        </div>
                                        <div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
                                            <div style="text-align: center; min-width: 85px;">
                                                <div style="font-size: 9px; color: #666; margin-bottom: 2px; text-transform: uppercase; font-weight: 600;">Rendimiento</div>
                                                <div style="font-size: 16px; font-weight: 700; color: #1a2332;">{performance}/6</div>
                                                <div style="background: #f0f0f0; border-radius: 3px; height: 5px; overflow: hidden; width: 65px; margin: 4px auto 0;">
                                                    <div style="background: #ff4444; height: 100%; width: {perf_percent}%;"></div>
                                                </div>
                                            </div>
                                            <div style="text-align: center; min-width: 85px;">
                                                <div style="font-size: 9px; color: #666; margin-bottom: 2px; text-transform: uppercase; font-weight: 600;">Potencial</div>
                                                <div style="font-size: 16px; font-weight: 700; color: #1a2332;">{potential}/6</div>
                                                <div style="background: #f0f0f0; border-radius: 3px; height: 5px; overflow: hidden; width: 65px; margin: 4px auto 0;">
                                                    <div style="background: #ff4444; height: 100%; width: {pot_percent}%;"></div>
                                                </div>
                                            </div>
                                            <div style="background: {conclusion_color}; color: white; padding: 8px 12px; border-radius: 6px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                                {conclusion_text}
                                            </div>
                                        </div>
                                    </div>
                                """
                                st.markdown(player_card_html, unsafe_allow_html=True)
                                
                                # VER and EDITAR buttons
                                edit_key = f"{player_key}_edit"
                                if edit_key not in st.session_state:
                                    st.session_state[edit_key] = False
                                
                                col_btn1, col_btn2, col_space = st.columns([1, 1, 7])
                                with col_btn1:
                                    if st.button("📝 VER" if not st.session_state[player_key] else "❌ CERRAR", key=f"btn_{player_key}", use_container_width=True):
                                        st.session_state[player_key] = not st.session_state[player_key]
                                        st.rerun()
                                with col_btn2:
                                    if st.button("✏️ EDITAR" if not st.session_state[edit_key] else "❌ CANCELAR", key=f"btn_edit_{player_key}", use_container_width=True):
                                        st.session_state[edit_key] = not st.session_state[edit_key]
                                        st.rerun()
                                
                                # EDIT MODE
                                if st.session_state[edit_key]:
                                    st.markdown("---")
                                    st.markdown("### ✏️ Editar Informe")
                                    
                                    # Match Information Section
                                    st.markdown("#### 📅 Información del Partido")
                                    col_m1, col_m2 = st.columns(2)
                                    
                                    with col_m1:
                                        # Get current date value
                                        current_date = report.get('Date', str(date.today()))
                                        try:
                                            if isinstance(current_date, str):
                                                date_value = pd.to_datetime(current_date).date()
                                            else:
                                                date_value = current_date
                                        except:
                                            date_value = date.today()
                                        
                                        new_date = st.date_input(
                                            "Fecha del Partido",
                                            value=date_value,
                                            key=f"date_{player_key}"
                                        )
                                    
                                    with col_m2:
                                        phase_options = ["Group Stage", "Round of 16", "Quarter Finals", "Semi Finals", "Final"]
                                        current_phase = report.get('Phase', 'Group Stage')
                                        phase_idx = phase_options.index(current_phase) if current_phase in phase_options else 0
                                        
                                        new_phase = st.selectbox(
                                            "Fase/Ronda",
                                            phase_options,
                                            index=phase_idx,
                                            key=f"phase_{player_key}"
                                        )
                                    
                                    st.markdown("---")
                                    
                                    # Player Information Section
                                    st.markdown("#### 👤 Información del Jugador")
                                    col_p1, col_p2, col_p3 = st.columns(3)
                                    
                                    with col_p1:
                                        new_number = st.number_input(
                                            "Número",
                                            min_value=1,
                                            max_value=99,
                                            value=int(player_number) if str(player_number).isdigit() else 1,
                                            key=f"number_{player_key}"
                                        )
                                    
                                    with col_p2:
                                        position_options = ["GK", "RB", "CB", "LB", "DM", "CM", "CAM", "RW", "LW", "ST"]
                                        current_position = str(player_position).strip()
                                        position_idx = position_options.index(current_position) if current_position in position_options else 0
                                        
                                        new_position = st.selectbox(
                                            "Posición",
                                            position_options,
                                            index=position_idx,
                                            key=f"position_{player_key}"
                                        )
                                    
                                    with col_p3:
                                        # Get birth year value
                                        birth_year_val = player_birth_year
                                        if birth_year_val and str(birth_year_val) not in ['nan', '', 'None']:
                                            try:
                                                birth_year_int = int(float(birth_year_val))
                                            except:
                                                birth_year_int = 2005
                                        else:
                                            birth_year_int = 2005
                                        
                                        new_birth_year = st.number_input(
                                            "Año de Nacimiento",
                                            min_value=1990,
                                            max_value=2015,
                                            value=birth_year_int,
                                            key=f"birth_year_{player_key}"
                                        )
                                    
                                    col_p4, col_p5 = st.columns(2)
                                    
                                    with col_p4:
                                        starter_options = ["Sí", "No"]
                                        current_starter = report.get('Starter', 'Sí')
                                        starter_idx = 0 if current_starter == 'Sí' else 1
                                        
                                        new_starter = st.selectbox(
                                            "Titular",
                                            starter_options,
                                            index=starter_idx,
                                            key=f"starter_{player_key}"
                                        )
                                    
                                    with col_p5:
                                        current_minutes = report.get('Minutes', 90)
                                        try:
                                            minutes_val = int(current_minutes)
                                        except:
                                            minutes_val = 90
                                        
                                        new_minutes = st.number_input(
                                            "Minutos Jugados",
                                            min_value=0,
                                            max_value=120,
                                            value=minutes_val,
                                            key=f"minutes_{player_key}"
                                        )
                                    
                                    st.markdown("---")
                                    
                                    # Performance Section
                                    st.markdown("#### ⚽ Rendimiento y Evaluación")
                                    col_e1, col_e2, col_e3 = st.columns(3)
                                    
                                    with col_e1:
                                        new_performance = st.number_input(
                                            "Rendimiento (1-6)",
                                            min_value=1.0,
                                            max_value=6.0,
                                            value=float(performance),
                                            step=0.5,
                                            key=f"perf_{player_key}"
                                        )
                                    
                                    with col_e2:
                                        new_potential = st.number_input(
                                            "Potencial (1-6)",
                                            min_value=1.0,
                                            max_value=6.0,
                                            value=float(potential),
                                            step=0.5,
                                            key=f"pot_{player_key}"
                                        )
                                    
                                    with col_e3:
                                        conclusion_options = [
                                            "A - Firmar (Sign)",
                                            "B+ - Seguir para Firmar (Follow to Sign)",
                                            "B - Seguir (Follow)"
                                        ]
                                        current_conclusion_idx = 0
                                        for idx, opt in enumerate(conclusion_options):
                                            if opt in str(conclusion):
                                                current_conclusion_idx = idx
                                                break
                                        
                                        new_conclusion = st.selectbox(
                                            "Conclusión",
                                            conclusion_options,
                                            index=current_conclusion_idx,
                                            key=f"concl_{player_key}"
                                        )
                                    
                                    new_report = st.text_area(
                                        "Report",
                                        value=str(full_report_text) if str(full_report_text) != 'nan' else '',
                                        height=150,
                                        key=f"report_{player_key}"
                                    )
                                    
                                    st.markdown("---")
                                    
                                    # Action buttons
                                    col_btn_save, col_btn_delete = st.columns([3, 1])
                                    
                                    with col_btn_save:
                                        # Save button
                                        if st.button("💾 GUARDAR CAMBIOS", key=f"save_{player_key}", type="primary", use_container_width=True):
                                            try:
                                                # Load current data from Google Sheets
                                                df_all_reports = read_google_sheet('fifa_u17_match_reports', 'Sheet1')
                                                
                                                # Find the exact row to update using multiple criteria
                                                mask = (
                                                    (df_all_reports['Scout'] == scout) &
                                                    (df_all_reports['Match'] == match_name) &
                                                    (df_all_reports[player_col] == player_name)
                                                )
                                                
                                                # Update all the values
                                                df_all_reports.loc[mask, 'Date'] = str(new_date)
                                                df_all_reports.loc[mask, 'Phase'] = new_phase
                                                df_all_reports.loc[mask, 'Number'] = new_number
                                                df_all_reports.loc[mask, 'Position'] = new_position
                                                df_all_reports.loc[mask, 'Birth Year'] = new_birth_year
                                                df_all_reports.loc[mask, 'Starter'] = new_starter
                                                df_all_reports.loc[mask, 'Minutes'] = new_minutes
                                                df_all_reports.loc[mask, 'Performance'] = new_performance
                                                df_all_reports.loc[mask, 'Potential'] = new_potential
                                                df_all_reports.loc[mask, 'Conclusion'] = new_conclusion
                                                df_all_reports.loc[mask, 'Report'] = new_report
                                                
                                                # Save back to Google Sheets
                                                write_google_sheet(df_all_reports, 'fifa_u17_match_reports', 'Sheet1')
                                                
                                                st.success("✅ Informe actualizado exitosamente!")
                                                st.session_state[edit_key] = False
                                                
                                                # Wait a moment and reload
                                                time.sleep(1)
                                                st.rerun()
                                                
                                            except Exception as e:
                                                st.error(f"❌ Error al guardar: {e}")
                                                st.warning("⚠️ Si otro scout está guardando informes, espera unos segundos e intenta de nuevo.")
                                    
                                    with col_btn_delete:
                                        # Delete button
                                        if st.button("🗑️ ELIMINAR", key=f"delete_{player_key}", type="secondary", use_container_width=True):
                                            # Show confirmation in session state
                                            confirm_key = f"confirm_delete_{player_key}"
                                            if confirm_key not in st.session_state:
                                                st.session_state[confirm_key] = True
                                                st.warning("⚠️ Haz clic de nuevo para confirmar la eliminación")
                                                st.rerun()
                                            else:
                                                try:
                                                    # Load current data from Google Sheets
                                                    df_all_reports = read_google_sheet('fifa_u17_match_reports', 'Sheet1')
                                                    
                                                    # Find the exact row to delete
                                                    mask = (
                                                        (df_all_reports['Scout'] == scout) &
                                                        (df_all_reports['Match'] == match_name) &
                                                        (df_all_reports[player_col] == player_name)
                                                    )
                                                    
                                                    # Remove the row
                                                    df_all_reports = df_all_reports[~mask]
                                                    
                                                    # Save back to Google Sheets
                                                    write_google_sheet(df_all_reports, 'fifa_u17_match_reports', 'Sheet1')
                                                    
                                                    st.success("✅ Informe eliminado exitosamente!")
                                                    
                                                    # Clear confirmation state
                                                    if confirm_key in st.session_state:
                                                        del st.session_state[confirm_key]
                                                    
                                                    # Wait a moment and reload
                                                    time.sleep(1)
                                                    st.rerun()
                                                    
                                                except Exception as e:
                                                    st.error(f"❌ Error al eliminar: {e}")
                                                    st.warning("⚠️ Si otro scout está guardando informes, espera unos segundos e intenta de nuevo.")
                                    
                                    st.markdown("---")
                                
                                # Expandable REPORT section (VIEW MODE)
                                elif st.session_state[player_key] and full_report_text and str(full_report_text) != 'nan':
                                    report_html = f"""
                                        <div style="background: #fffef0; border: 2px solid #FFC60A; border-radius: 8px; padding: 25px; margin-bottom: 15px;">
                                            <h4 style="color: #1a2332; margin: 0 0 15px 0; font-size: 16px; border-bottom: 2px solid #FFC60A; padding-bottom: 10px;">📝 REPORT</h4>
                                            <div style="font-size: 14px; color: #333; line-height: 1.8;">
                                                {full_report_text}
                                            </div>
                                        </div>
                                    """
                                    st.markdown(report_html, unsafe_allow_html=True)

# Helper functions
def show_login_page():
    # Users database
    USERS = {
        'juangambero': {
            'password': 'juanito',
            'name': 'Juan Gambero',
            'photo': 'juan.png'
        },
        'rafagil': {
            'password': 'rafita',
            'name': 'Rafa Gil',
            'photo': 'rafa.png'
        },
        'alvarolopez': {
            'password': 'alvarito',
            'name': 'Alvaro Lopez',
            'photo': 'alvaro.png'
        },
        'scoutingdepartment': {
            'password': 'scouting',
            'name': 'Scouting Department',
            'photo': 'alnassr.png'
        }
    }
    
    # Custom CSS for login page
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Load Al Nassr logo for login
        try:
            from PIL import Image
            import io
            logo_login = Image.open('alnassr.png')
            logo_login.thumbnail((40, 40))
            buffered_login = io.BytesIO()
            if logo_login.mode in ('RGBA', 'LA', 'P'):
                logo_login.save(buffered_login, format="PNG")
            else:
                logo_login = logo_login.convert('RGB')
                logo_login.save(buffered_login, format="PNG")
            logo_login_str = base64.b64encode(buffered_login.getvalue()).decode()
            logo_login_html = f'<img src="data:image/png;base64,{logo_login_str}" style="height:35px; vertical-align:middle; margin-right:10px;">'
        except:
            logo_login_html = '🔐'
        
        st.markdown(f"### {logo_login_html} FIFA U17 Scouting", unsafe_allow_html=True)
        st.markdown("#### Login / تسجيل الدخول")
        
        # Login form
        username = st.text_input("👤 Username / اسم المستخدم", key="login_username")
        password = st.text_input("🔑 Password / كلمة المرور", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Login / دخول", use_container_width=True):
                if username in USERS and USERS[username]['password'] == password:
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.session_state.user_name = USERS[username]['name']
                    st.session_state.user_photo = USERS[username]['photo']
                    st.success(f"✅ Welcome {USERS[username]['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password / اسم المستخدم أو كلمة المرور غير صحيحة")
        
        with col_btn2:
            if st.button("🔄 Clear / مسح", use_container_width=True):
                st.rerun()
        
        # Info section
        st.markdown("---")
        st.info("🔒 Secure access for FIFA U17 scouts only")

def toggle_language():
    """Toggle between English and Arabic"""
    if st.session_state.language == 'en':
        st.session_state.language = 'ar'
    else:
        st.session_state.language = 'en'
    st.rerun()

def logout():
    """Logout function to clear session state"""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.user_name = None
    st.session_state.user_photo = None
    st.rerun()

def apply_custom_css():
    st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    </style>
    """, unsafe_allow_html=True)

def create_download_buttons(df, filename_base, label_prefix):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"{label_prefix} CSV",
        data=csv,
        file_name=f"{filename_base}.csv",
        mime="text/csv"
    )

# Country flags mapping
COUNTRY_FLAGS = {}

if __name__ == "__main__":
    main()
