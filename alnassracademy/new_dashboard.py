import streamlit as st
import pandas as pd
import base64
from PIL import Image
import io
from datetime import date

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

# Page configuration
st.set_page_config(
    page_title="Al Nassr Academy - Scouting Department",
    page_icon="alnassracademy.png",
    layout="wide"
)

# Custom CSS for buttons and layout
st.markdown("""
<style>
/* Fondo principal blanco y texto azul marino */
.stApp, .main, .block-container, .stAppViewContainer {
    background-color: white !important;
    color: #002B5B !important;
}

/* Títulos y texto general en azul marino */
h1, h2, h3, h4, h5, h6, p, div, span {
    color: #002B5B !important;
}

/* Contenido de Streamlet */
.stMarkdown, .stText, .stTextInput, .stSelectbox, .stTextArea, .stDateInput, .stNumberInput, .stRadio, .stCheckbox {
    color: #002B5B !important;
}

/* Button styles */
.stButton > button {
    background: #F9D342 !important;  /* Fondo amarillo Al Nassr */
    color: #002B5B !important;       /* Texto azul marino */
    border: 2px solid #000000 !important;
    border-radius: 15px !important;
    padding: 2rem !important;
    font-weight: bold !important;
    font-size: 1.1rem !important;
    height: 180px !important;
    transition: all 0.3s ease !important;
    white-space: pre-line !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    margin: 0 !important;
}

.stButton > button:hover {
    background: #002B5B !important;  /* Azul marino al hover */
    color: #F9D342 !important;       /* Amarillo al hover */
}

/* Títulos en negrita */
.stButton > button div {
    font-weight: 700 !important;     /* Títulos extra negrita */
    line-height: 1.4 !important;
    font-size: 1.3rem !important;    /* Tamaño de fuente ligeramente más grande */
}

/* Table styles */
.stDataFrame {
    border: 1px solid #F9D342 !important;
    border-radius: 8px !important;
}

.stDataFrame th {
    background-color: #002B5B !important;
    color: #F9D342 !important;
}

/* Header styles */
.main-header {
    text-align: center;
    margin-bottom: 2.5rem;
    padding: 1.5rem 0;
    background: linear-gradient(135deg, #002B5B 0%, #1e4d7b 100%) !important;
    color: #F9D342 !important;  /* Texto amarillo en el header */
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Títulos dentro del header en amarillo */
.main-header h1,
.main-header h2,
.main-header h3,
.main-header p {
    color: #F9D342 !important;
}

.logo-container {
    display: flex;
    justify-content: center;
    margin-bottom: 1rem;
}

.logo-container img {
    border-radius: 50%;
    border: 3px solid #F9D342;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0.5rem 0;
    letter-spacing: 1px;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
}

.sub-title {
    font-size: 1.2rem;
    margin: 0.5rem 0;
    color: #FFFFFF;
    font-weight: 500;
}

.dashboard-subtitle {
    font-size: 1.5rem;
    margin: 1rem 0 0;
    color: #F9D342;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_teams_data():
    try:
        # Load only the Teams sheet
        df = pd.read_excel("Saudi_Youth_Leagues.xlsx", sheet_name='Teams')
        return df
    except Exception as e:
        st.error(f"Error loading teams data: {e}")
        return pd.DataFrame()

def load_u21_squad():
    try:
        # Load the SquadU21 sheet
        df = pd.read_excel("Saudi_Youth_Leagues.xlsx", sheet_name='SquadU21')
        return df
    except Exception as e:
        st.error(f"Error loading U21 squad data: {e}")
        return pd.DataFrame()

def show_create_report_page():
    # Header with back button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("← Back", key="back_btn_create"):
            st.session_state.current_page = 'dashboard'
            st.rerun()
    
    st.header("📝 New Player Assessment")
    st.markdown("Fill out the form below to create a new scouting report")
    
    # Formulario con todos los campos del scouting original
    with st.form("scout_report_form", clear_on_submit=True):
        # Información Básica
        st.subheader("📝 Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            scout_name = st.text_input("Scout Name *", placeholder="Your name")
            player_name = st.text_input("Player Name *", placeholder="Full player name")
            report_date = st.date_input("Report Date *", value=date.today())
        
        with col2:
            shirt_number = st.text_input("T-Shirt Number", placeholder="e.g., 10")
            birth_year = st.number_input("Birth Year *", min_value=2004, max_value=2015, value=2006)
            nationality = st.text_input("Nationality *", placeholder="e.g., Saudi Arabia")
        
        # Competición y Equipo
        st.subheader("⚽ Competition & Team")
        col1, col2 = st.columns(2)
        
        with col1:
            # Opciones de ligas juveniles
            league_options = [
                "Saudi U-18 Premier League",
                "Saudi U-17 Premier League", 
                "Saudi U-16 Premier League",
                "Saudi U-15 Premier League",
                "Saudi Elite League U-21"
            ]
            league = st.selectbox("League - Category *", options=league_options)
            match_date = st.date_input("Match Date *", value=date.today())
        
        with col2:
            # Cargar equipos de la liga seleccionada
            if league == "Saudi Elite League U-21":
                teams = [
                    "Al-Bukayriyah FC", "Al-Nassr FC", "Al-Adalah FC", "Al-Ittihad Club", "Al-Ahli Saudi FC",
                    "NEOM Club", "Al-Riyadh SC", "Al-Fayha FC", "Al-Wehda FC", "Al-Taawoun FC",
                    "Khaleej FC", "Al-Okhdood FC", "Al-Jabalain", "Al-Hilal SFC", "Al-Shabab FC",
                    "Al-Hazem FC", "Al-Raed FC", "Al-Kholood Club", "Al-Qadsiah FC", "Al-Najmah SC",
                    "Al-Fateh SC", "Damac FC", "Al-Orobah FC", "Ettifaq FC"
                ]
            else:
                # Cargar equipos de otras ligas desde Excel
                try:
                    df = pd.read_excel("Saudi_Youth_Leagues.xlsx")
                    teams = df[df['League'] == league]['Team Name'].unique().tolist()
                except Exception as e:
                    st.error(f"Error loading teams: {e}")
                    teams = []
            
            player_team = st.selectbox("Player Team *", 
                                    options=sorted(teams) if teams else ["No teams available"],
                                    placeholder="Select a team")
            
            position_options = ["GK", "RB", "RWB", "CB", "LB", "LWB", 
                              "DM/6", "CM/8", "AM/10", "RW/WF", "LW/WF", "ST/9", "SS/9.5"]
            position = st.selectbox("Position *", options=position_options)
        
        # Pie dominante
        foot = st.selectbox("Dominant Foot *", options=["Right", "Left", "Both"])
        
        # Información adicional
        col1, col2 = st.columns(2)
        with col1:
            contract = st.text_input("Contract (if available)")
        with col2:
            agent = st.text_input("Agent (if available)")
        
        # Evaluación inteligente
        smart_eval = st.text_area("Smart Evaluation *", 
                                placeholder="Clear analysis: behavior, impacts, key data, tactical context...",
                                height=120)
        
        # RATINGS 1-3
        st.subheader("📊 Performance Ratings")
        st.caption("Scale 1-3 where 3 is outstanding performance")
        
        col1, col2 = st.columns(2)
        with col1:
            performance = st.radio("Performance Rating *", options=[1, 2, 3], horizontal=True)
        with col2:
            potential = st.radio("Potential Rating *", options=[1, 2, 3], horizontal=True)
        
        # Conclusión
        conclusion = st.selectbox("Conclusion *", 
                                options=["SIGN (التوقيع معه)", "MONITOR CLOSELY (متابعة دقيقة)", "DISCARD (الاستبعاد)"])
        
        # Botón submit
        submitted = st.form_submit_button("Submit Report", use_container_width=True)
        
        if submitted:
            # Validación
            required_fields = [scout_name, player_name, league, player_team, position, foot, smart_eval]
            if all(required_fields) and player_team != "No teams available":
                # Crear diccionario con los datos
                report_data = {
                    'scout_name': scout_name,
                    'player_name': player_name,
                    'report_date': report_date,
                    'shirt_number': shirt_number,
                    'birth_year': birth_year,
                    'nationality': nationality,
                    'league': league,
                    'match_date': match_date,
                    'team': player_team,
                    'position': position,
                    'foot': foot,
                    'contract': contract,
                    'agent': agent,
                    'evaluation': smart_eval,
                    'performance': performance,
                    'potential': potential,
                    'conclusion': conclusion,
                    'created_at': date.today().isoformat()
                }
                
                # Aquí iría el código para guardar en base de datos
                try:
                    # Cargar datos existentes o crear nuevo DataFrame
                    try:
                        reports_df = pd.read_excel('scouting_reports.xlsx')
                    except FileNotFoundError:
                        reports_df = pd.DataFrame(columns=report_data.keys())
                    
                    # Añadir nuevo reporte
                    new_report = pd.DataFrame([report_data])
                    reports_df = pd.concat([reports_df, new_report], ignore_index=True)
                    
                    # Guardar en Excel
                    reports_df.to_excel('scouting_reports.xlsx', index=False)
                    st.success("✅ Report saved successfully!")
                except Exception as e:
                    st.error(f"Error saving report: {e}")
            else:
                st.error("Please fill all required fields (*)")

def show_leagues_teams_page():
    # Team logos mapping with full paths - verified filenames
    team_logos = {
        "Al-Bukayriyah FC": "albukiryahfc.png",  # Verified filename
        "Al-Nassr FC": "alnassr.png", 
        "Al-Adalah FC": "aladalahclub.png",  # Verified filename
        "Al-Ittihad Club": "alittihad.png",
        "Al-Ahli Saudi FC": "alahli.png",
        "NEOM Club": "neom.png",
        "Al-Riyadh SC": "alriyadh.png",
        "Al-Fayha FC": "alfayha.png",
        # Note: Al-Wehda FC logo file not found - using fallback
        "Al-Orobah FC": "AlOrobah.png",  # Note capital A in filename
        "Al-Taawoun FC": "altaawoun.png",
        "Khaleej FC": "alkhaleej.png",
        "Al-Okhdood FC": "alokhdood.png",
        # Note: Al-Jabalain logo file not found - using fallback
        "Al-Hilal SFC": "alhilal.png",
        "Al-Shabab FC": "alshabab.png",
        "Al-Hazem FC": "alhazem.png",
        "Al-Raed FC": "alraed.png",
        "Al-Kholood Club": "alkholood.png",
        "Al-Qadsiah FC": "alqadsiah.png",
        "Al-Najmah SC": "alnajma.png",
        "Al-Fateh SC": "alfateh.png",
        "Damac FC": "damac.png",
        "Ettifaq FC": "alettifaq.png"
    }
    
    # Header with back button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("← Back", key="back_btn_leagues"):
            st.session_state.current_page = 'dashboard'
            st.rerun()
    
    st.header("🏆 Leagues & Teams")
    
    # Theme configuration
    if 'theme' not in st.session_state:
        st.session_state.theme = "🌞 Light"
    
    # Theme toggle in sidebar
    new_theme = st.sidebar.radio("Theme", ["🌞 Light", "🌙 Dark"], 
                               index=0 if st.session_state.theme == "🌞 Light" else 1,
                               key="theme_selector")
    
    # Update theme if changed
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()
    
    # Define theme colors
    if st.session_state.theme == "🌙 Dark":
        theme_colors = {
            "bg": "#0E1117",
            "text": "#FFFFFF",
            "secondary_bg": "#1E1E1E",
            "border": "#2D3748",
            "hover": "#2D3748",
            "input_bg": "#1E1E1E",
            "input_text": "#FFFFFF",
            "input_border": "#2D3748",
            "player_hover": "#1E1E1E",
            "interesting_bg": "rgba(255, 165, 0, 0.2)",
            "interesting_border": "#FFA500",
            "improvement_bg": "rgba(30, 144, 255, 0.2)",
            "improvement_border": "#1E90FF",
            "top_bg": "rgba(46, 204, 64, 0.2)",
            "top_border": "#2ECC40"
        }
    else:
        theme_colors = {
            "bg": "#FFFFFF",
            "text": "#000000",
            "secondary_bg": "#F8F9FA",
            "border": "#E2E8F0",
            "hover": "#E2E8F0",
            "input_bg": "#FFFFFF",
            "input_text": "#000000",
            "input_border": "#E2E8F0",
            "player_hover": "#F8F9FA",
            "interesting_bg": "#FFE4B5",
            "interesting_border": "#FFA500",
            "improvement_bg": "#E6F0FF",
            "improvement_border": "#1E90FF",
            "top_bg": "#E6FFE6",
            "top_border": "#228B22"
        }
    
    # Apply theme
    st.markdown(f"""
    <style>
    /* Base styles */
    .stApp {{
        background-color: {theme_colors['bg']};
        color: {theme_colors['text']};
    }}
    
    /* Main content area */
    .main {{
        background-color: {theme_colors['bg']};
        color: {theme_colors['text']};
    }}
    
    /* Player rows */
    .player-row {{
        border-bottom: 1px solid {theme_colors['border']};
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        transition: all 0.3s ease;
    }}
    
    .player-row:hover {{
        background-color: {theme_colors['player_hover']};
    }}
    
    /* Player evaluation styles */
    .player-interesting {{
        background-color: {theme_colors['interesting_bg']} !important;
        border-left: 5px solid {theme_colors['interesting_border']} !important;
    }}
    
    .player-improvement {{
        background-color: {theme_colors['improvement_bg']} !important;
        border-left: 5px solid {theme_colors['improvement_border']} !important;
    }}
    
    .player-top {{
        background-color: {theme_colors['top_bg']} !important;
        border-left: 5px solid {theme_colors['top_border']} !important;
    }}
    
    /* Form elements */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>select,
    .stTextArea>div>textarea {{
        background-color: {theme_colors['input_bg']} !important;
        color: {theme_colors['input_text']} !important;
        border-color: {theme_colors['input_border']} !important;
    }}
    
    /* Tables */
    table {{
        color: {theme_colors['text']};
    }}
    
    /* Ensure text is visible in inputs */
    .stTextInput input, 
    .stTextArea textarea,
    .stSelectbox select {{
        color: {theme_colors['input_text']} !important;
    }}
    
    /* Fix for select box text color in dark mode */
    .stSelectbox>div>div>div>div {{
        color: {theme_colors['input_text']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Additional player evaluation styling
    st.markdown("""
    <style>
    /* Player row styling */
    .player-row {
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    .player-row:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Evaluation styles */
    .player-interesting {
        background-color: rgba(255, 140, 0, 0.15) !important;
        border-left: 5px solid #FF8C00 !important;
    }

    .player-improvement {
        background-color: rgba(30, 144, 255, 0.15) !important;
        border-left: 5px solid #1E90FF !important;
    }

    .player-top {
        background-color: rgba(34, 139, 34, 0.15) !important;
        border-left: 5px solid #228B22 !important;
    }
    
    /* Evaluation indicator */
    .evaluation-indicator {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-block;
        margin: 0 auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Form elements */
    .stSelectbox, .stTextInput {
        margin-bottom: 0 !important;
    }
    
    /* Make sure columns are properly spaced */
    .stContainer > div {
        padding: 4px 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    try:
        # Load both sheets
        teams_df = pd.read_excel("Saudi_Youth_Leagues.xlsx", sheet_name="Teams")
        players_df = pd.read_excel('Saudi_Youth_Leagues.xlsx', sheet_name='SquadU21')
        players_df['evaluation'] = players_df['evaluation'].fillna('')  # Ensure empty evaluations are empty strings
        
        # Ensure National_Caps column exists
        if 'National_Caps' not in players_df.columns:
            players_df['National_Caps'] = 0
        
        # Add evaluation columns if they don't exist
        if 'evaluation' not in players_df.columns:
            players_df['evaluation'] = ''
        if 'notes' not in players_df.columns:
            players_df['notes'] = ''
            
        # Define evaluation categories and colors
        evaluation_colors = {
            "": {"color": "#FFFFFF", "label": "Not Evaluated", "class": ""},
            "INTERESTING": {"color": "#FF8C00", "label": "🟠 Interesting Player", "class": "evaluation-row-interesting"},
            "IMPROVEMENT": {"color": "#1E90FF", "label": "🔵 Needs Improvement", "class": "evaluation-row-improvement"},
            "TOP_POTENTIAL": {"color": "#228B22", "label": "🟢 Top Potential", "class": "evaluation-row-top"}
        }
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Main layout: Filters | Content
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Filters")
        
        # 1. League filter
        league_options = sorted(teams_df['League'].unique())
        selected_league = st.selectbox(
            "Select League:",
            options=league_options,
            key="league_selector"
        )
        
        # 2. Team filter
        league_teams = teams_df[teams_df['League'] == selected_league]
        team_options = ["All Teams"] + sorted(league_teams['Team Name'].unique().tolist())
        
        if 'team_selector' not in st.session_state:
            st.session_state.team_selector = "All Teams"
        if st.session_state.team_selector not in team_options:
            st.session_state.team_selector = "All Teams"
            
        selected_team = st.selectbox(
            "Select Team:",
            options=team_options,
            index=team_options.index(st.session_state.team_selector),
            key=f"team_selector_{selected_league}"
        )
        
        # Update session state when dropdown changes
        if selected_team != st.session_state.team_selector:
            st.session_state.team_selector = selected_team
            st.rerun()
        
        # 3. Player search (only for U21)
        if selected_league == "Saudi Elite League U-21":
            search_player = st.text_input(
                "Search Player:", 
                placeholder="Type player name...",
                key="player_search"
            )
        
        # Metrics
        st.metric("Teams in League", len(league_teams))
        if selected_league == "Saudi Elite League U-21":
            st.metric("Total U21 Players", len(players_df))
    
    with col2:
        # No title for Teams section - goes straight to the table
            
        # Filter teams by selected league
        league_teams = teams_df[teams_df['League'] == selected_league].copy()
        
        # If a specific team is selected, show only that team
        if st.session_state.team_selector != "All Teams":
            league_teams = league_teams[league_teams['Team Name'] == st.session_state.team_selector]
            
        # Add logo column to teams table
        def get_team_logo_path(team_name):
            return team_logos.get(team_name, "")
            
        st.subheader("Teams")
        
        # Tiny Back to All Teams button - only show when a team is selected
        if st.session_state.team_selector != "All Teams":
            if st.button("🔄 Back to All Teams", 
                       key=f"back_all_teams_{selected_league}", 
                       help="Show all teams"):
                st.session_state.team_selector = "All Teams"
                st.rerun()
            st.write("")
            
        # Table headers
        col1, col2, col3 = st.columns([1, 4, 4])
        with col1:
            st.write("**Select**")
        with col2:
            st.write("**Team Name**")
        with col3:
            st.write("**League**")
            
        st.divider()
            
        # Display each team in a row with logo, name, and league
        for _, team in league_teams.iterrows():
            col1, col2, col3 = st.columns([1, 4, 4])
            team_name = team['Team Name']
                
            with col1:
                # Simple emoji button for team selection
                if st.button(f"📋", key=f"select_{team_name}", help=f"Select {team_name}"):
                    st.session_state.team_selector = team_name
                    st.rerun()
                
            with col2:
                # Column for Team Name
                st.write(f"**{team_name}**")
                
            with col3:
                # Column for League
                st.write(team['League'])
                
                # Add a subtle divider between teams
                st.divider()
        
        # Only if U21, ALSO show players
        if selected_league == "Saudi Elite League U-21" and not players_df.empty:
            filtered_players = players_df.copy()
            
            # Filter by team using session state
            if st.session_state.team_selector != "All Teams":
                filtered_players = filtered_players[filtered_players['Team'] == st.session_state.team_selector]
            
            # Filter by search
            if 'search_player' in locals() and search_player:
                filtered_players = filtered_players[
                    filtered_players['Name'].str.contains(search_player, case=False, na=False)
                ]
            
            # Show players section with team name and logo if a specific team is selected
            if st.session_state.team_selector != "All Teams" and st.session_state.team_selector in team_logos:
                player_col1, player_col2 = st.columns([1, 10])
                with player_col1:
                    st.image(team_logos[st.session_state.team_selector], width=50)
                with player_col2:
                    st.subheader(f"Players - {st.session_state.team_selector}")
                    
                    # Add column headers
                    header_cols = st.columns([1, 3, 2, 1.5, 1.5, 2, 3])
                    with header_cols[0]:
                        st.write("**Num.**")
                    with header_cols[1]:
                        st.write("**Player Name**")
                    with header_cols[2]:
                        st.write("**Position**")
                    with header_cols[3]:
                        st.write("**Year**")
                    with header_cols[4]:
                        st.write("**KSA Caps**")
                    with header_cols[5]:
                        st.write("**Evaluation**")
                    with header_cols[6]:
                        st.write("**Notes**")
                    
                    # Create a form for player edits
                    with st.form(key='player_edits_form'):
                        for idx, player in filtered_players.iterrows():
                            # Get current evaluation and notes
                            current_eval = player.get('evaluation', '')
                            current_notes = player.get('notes', '')
                            
                            # Determine CSS class based on evaluation
                            css_class = ""
                            if current_eval == "INTERESTING":
                                css_class = "player-interesting"
                            elif current_eval == "IMPROVEMENT":
                                css_class = "player-improvement"
                            elif current_eval == "TOP_POTENTIAL":
                                css_class = "player-top"
                        
                            # Define position options
                            position_options = ["GK", "DF", "MF", "FW", "LB", "RB", "CB", "DM", "CM", "CAM", "RW", "LW", "ST"]
                            
                            # Create player row container with CSS class
                            st.markdown(f'<div class="player-row {css_class}">', unsafe_allow_html=True)
                            
                            # Create columns for the player row - 7 columns in total
                            # [0] Number, [1] Player Name, [2] Position, 
                            # [3] Year of Birth, [4] KSA Caps, [5] Evaluation, [6] Notes
                            cols = st.columns([1, 3, 2, 1.5, 1.5, 2, 3])
                            
                            with cols[0]:
                                st.write(f"**{player['Number']}**")
                                
                            with cols[1]:
                                # Display player name with color indicator
                                color_map = {
                                    "INTERESTING": "#FF8C00",
                                    "IMPROVEMENT": "#1E90FF",
                                    "TOP_POTENTIAL": "#228B22",
                                    "": "transparent"
                                }
                                # Get the evaluation value
                                eval_key = f"eval_{idx}"
                                current_eval = player.get('evaluation', '')
                                if eval_key in st.session_state:
                                    current_eval = st.session_state[eval_key]
                                color = color_map.get(current_eval, "transparent")
                                st.markdown(
                                    f'<div style="display: flex; align-items: center; gap: 10px;">'
                                    f'<div style="width: 8px; height: 8px; border-radius: 50%; background-color: {color};"></div>'
                                    f'<span>{player["Name"]}</span>'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )
                                
                            with cols[3]:
                                # Position dropdown
                                pos_key = f"pos_{idx}"
                                current_pos = player['Position'] if player['Position'] in position_options else position_options[0]
                                selected_pos = st.selectbox(
                                    "Position",
                                    options=position_options,
                                    index=position_options.index(current_pos) if current_pos in position_options else 0,
                                    key=pos_key,
                                    label_visibility="collapsed"
                                )
                                
                            with cols[3]:
                                st.write(player['Year of Birth'])
                                
                            with cols[4]:
                                # KSA caps input
                                caps_key = f"caps_{idx}"
                                current_caps = player.get('National_Caps', '')
                                caps = st.text_input(
                                    "KSA Caps",
                                    value=str(current_caps) if pd.notna(current_caps) else "",
                                    key=caps_key,
                                    label_visibility="collapsed",
                                    placeholder="0"
                                )
                                
                            with cols[5]:
                                # Evaluation dropdown with color indicators
                                eval_key = f"eval_{idx}"
                                eval_options = ["", "INTERESTING", "IMPROVEMENT", "TOP_POTENTIAL"]
                                eval_labels = {
                                    "": "Not Evaluated",
                                    "INTERESTING": "🟠 Interesting Player",
                                    "IMPROVEMENT": "🔵 Needs Improvement",
                                    "TOP_POTENTIAL": "🟢 Top Potential"
                                }
                                
                                # Get current evaluation from session state or player data
                                current_eval = player.get('evaluation', '')
                                if eval_key in st.session_state:
                                    current_eval = st.session_state[eval_key]
                                
                                # Create the selectbox
                                selected_eval = st.selectbox(
                                    "Evaluation",
                                    options=eval_options,
                                    format_func=lambda x: eval_labels.get(x, x),
                                    index=eval_options.index(current_eval) if current_eval in eval_options else 0,
                                    key=eval_key,
                                    label_visibility="collapsed"
                                )
                                
                            with cols[6]:
                                # Notes field
                                notes_key = f"notes_{idx}"
                                notes = st.text_input(
                                    "Notes",
                                    value=current_notes,
                                    key=notes_key,
                                    label_visibility="collapsed",
                                    placeholder="Add notes..."
                                )
                        
                            # Close the player row div
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                            # Update position and caps in the dataframe
                            if pos_key in st.session_state:
                                players_df.at[idx, 'Position'] = st.session_state[pos_key]
                            if caps_key in st.session_state and st.session_state[caps_key]:
                                try:
                                    players_df.at[idx, 'National_Caps'] = int(st.session_state[caps_key])
                                except (ValueError, TypeError):
                                    players_df.at[idx, 'National_Caps'] = 0
                        
                        # Save button inside the form but outside the player loop
                        if st.form_submit_button("💾 Save Evaluations", use_container_width=True):
                            # Update the players_df with the new evaluations, notes, and internal numbers
                            for idx in filtered_players.index:
                                eval_key = f"eval_{idx}"
                                notes_key = f"notes_{idx}"
                                int_num_key = f"int_num_{idx}"
                                
                                if eval_key in st.session_state:
                                    players_df.at[idx, 'evaluation'] = st.session_state[eval_key]
                                if notes_key in st.session_state:
                                    players_df.at[idx, 'notes'] = st.session_state[notes_key]
                                if int_num_key in st.session_state:
                                    players_df.at[idx, 'Int_Number'] = st.session_state[int_num_key]
                            
                            # Save back to Excel
                            try:
                                with pd.ExcelWriter("Saudi_Youth_Leagues.xlsx", engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                                    players_df.to_excel(writer, sheet_name='SquadU21', index=False)
                                st.success("✅ Evaluations saved successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error saving evaluations: {e}")
                
                # Show number of players being displayed
                st.info(f"Showing {len(filtered_players)} players")
            else:
                st.info("No players found matching the criteria")

def get_team_logo(team_name):
    """Maps team names to their logo files."""
    # Normalize team names for matching
    team_name = team_name.lower().replace(' ', '').replace('-', '').replace('.', '').replace('fc', '').strip()
    
    # Map of team name variations to logo files
    team_logos = {
        'alnassr': 'alnassr.png',
        'alhilal': 'alhilal.png',
        'alittihad': 'alittihad.png',
        'alshabab': 'alshabab.png',
        'alnassracademy': 'alnassracademy.png',
        'aljabalain': 'aljabalain.png',
        'aljabalin': 'aljabalain.png',  # Alias for Al-Jabalain
        'aladalah': 'aladalahclub.png',
        'alahli': 'alahli.png',
        'albukiryah': 'albukiryahfc.png',
        'alettifaq': 'alettifaq.png',
        'alfateh': 'alfateh.png',
        'alfayha': 'alfayha.png',
        'alhazem': 'alhazem.png',
        'alkhaleej': 'alkhaleej.png',
        'alkholood': 'alkholood.png',
        'alnajma': 'alnajma.png',
        'alokhdood': 'alokhdood.png',
        'alqadsiah': 'alqadsiah.png',
        'alraed': 'alraed.png',
        'alriyadh': 'alriyadh.png',
        'altaawoun': 'altaawoun.png',
        'damac': 'damac.png',
        'neom': 'neom.png',
        'alorobah': 'AlOrobah.png'
    }
    
    # Try to find a matching logo
    for key, logo in team_logos.items():
        if key in team_name:
            return logo
    
    # Default logo if no match found
    return 'alnassr.png'  # Default to Al-Nassr logo or any other default

def show_calendar():
    st.header("📅 Match Calendar")
    
    # Add a refresh button to update the calendar
    if st.button("🔄 Refresh Calendar", key="refresh_calendar"):
        st.cache_data.clear()
        st.rerun()
    
    # Add a loading spinner while fetching data
    with st.spinner("Loading match calendar..."):
        try:
            # Import the scrape function
            from saff import scrape_full_schedule
            
            # URL for the U-21 league matches
            url = 'https://www.saff.com.sa/en/championship.php?id=350&type=all'
            
            # Scrape the match data
            matches = scrape_full_schedule(url)
            
            if not matches:
                st.warning("No match data available. Please try again later.")
                return
            
            # Convert to DataFrame for better display
            import pandas as pd
            df_matches = pd.DataFrame(matches)
            
            # Clean up the data
            if not df_matches.empty:
                # Remove any duplicate matches
                df_matches = df_matches.drop_duplicates()
                
                # Convert date to datetime for sorting
                try:
                    df_matches['date'] = pd.to_datetime(df_matches['date'], errors='coerce')
                    df_matches = df_matches.sort_values('date')
                    
                    # Format date for display
                    df_matches['date'] = df_matches['date'].dt.strftime('%Y-%m-%d')
                except Exception as e:
                    st.warning(f"Could not parse dates: {e}")
                
                # Display the matches in a nice format with team logos
                st.markdown("### Upcoming Matches")
                
                # Add some CSS to style the team logos and names
                st.markdown("""
                <style>
                .team-display {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    margin: 4px 0;
                }
                .team-logo {
                    width: 24px;
                    height: 24px;
                    object-fit: contain;
                }
                .match-row {
                    margin-bottom: 12px;
                    padding-bottom: 12px;
                    border-bottom: 1px solid #e0e0e0;
                }
                .match-row:last-child {
                    border-bottom: none;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Group by date
                for date, matches_on_date in df_matches.groupby('date'):
                    with st.expander(f"📅 {date} ({len(matches_on_date)} matches)"):
                        for _, match in matches_on_date.iterrows():
                            # Get team logos
                            home_logo = get_team_logo(match['home_team'])
                            away_logo = get_team_logo(match['away_team'])
                            
                            # Create columns for the match
                            col1, col2, col3 = st.columns([4, 1, 4])
                            
                            with col1:
                                # Home team with logo
                                st.markdown(f"""
                                <div class='team-display' style='justify-content: flex-end; text-align: right;'>
                                    <span><strong>{match['home_team']}</strong></span>
                                    <img src='data:image/png;base64,{0}' class='team-logo' alt='{1}'>
                                </div>
                                """.format(
                                    base64.b64encode(open(home_logo, 'rb').read()).decode() if home_logo else '',
                                    match['home_team']
                                ), unsafe_allow_html=True)
                            
                            with col2:
                                # Score or vs
                                st.markdown(f"<div style='text-align: center; padding-top: 4px;'><strong>{match['score'] if match['score'].strip() else 'vs'}</strong></div>", 
                                          unsafe_allow_html=True)
                            
                            with col3:
                                # Away team with logo
                                st.markdown(f"""
                                <div class='team-display'>
                                    <img src='data:image/png;base64,{0}' class='team-logo' alt='{1}'>
                                    <span><strong>{match['away_team']}</strong></span>
                                </div>
                                """.format(
                                    base64.b64encode(open(away_logo, 'rb').read()).decode() if away_logo else '',
                                    match['away_team']
                                ), unsafe_allow_html=True)
                            
                            # Add match details
                            st.caption(f"⏰ {match['time']} | 🏟️ {match['stadium']} | 📅 {match['week']}")
                            st.markdown("<div class='match-row'></div>", unsafe_allow_html=True)
                
                # Show raw data in an expander for debugging
                with st.expander("View Raw Data"):
                    st.dataframe(df_matches, use_container_width=True)
            
            else:
                st.warning("No matches found in the calendar.")
                
        except Exception as e:
            st.error(f"Error loading match calendar: {str(e)}")
            st.error("Please check your internet connection and try again.")

def show_leagues_section():
    st.markdown("## Leagues & Teams")
    df = load_teams_data()
    
    if not df.empty:
        # League filter
        league_filter = st.selectbox("Select League:", df['League'].unique())
        filtered_teams = df[df['League'] == league_filter]
        
        # Display teams in a table
        st.dataframe(filtered_teams, use_container_width=True)
    else:
        st.warning("No data available. Please check the Excel file.")

def show_dashboard():
    # Header section with logo and title
    st.markdown("""
    <div class="main-header">
        <div class="logo-container">
            <img src="data:image/png;base64,{0}" width="120">
        </div>
        <h1 class="main-title">AL NASSR ACADEMY</h1>
        <p class="sub-title">Scouting Department</p>
    </div>
    """.format(base64.b64encode(open('alnassracademy.png', 'rb').read()).decode()), unsafe_allow_html=True)
    
    # First row - 3 cards
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📝\n\nCreate Report\n\nCreate a new scouting report", 
                    key="create_report_btn",
                    use_container_width=True):
            st.session_state.current_page = 'create_report'
            st.rerun()
    
    with col2:
        if st.button("📋\n\nReports\n\nView existing scouting reports", 
                    key="reports_btn",
                    use_container_width=True):
            st.session_state.current_page = 'reports'
            st.rerun()
    
    with col3:
        if st.button("📊\n\nAnalytics\n\nView scouting analytics", 
                    key="analytics_btn",
                    use_container_width=True):
            st.session_state.current_page = 'analytics'
            st.rerun()
    
    # Second row - 2 cards
    col4, col5 = st.columns(2)
    
    with col4:
        if st.button("🏆\n\nLeagues & Teams\n\nManage leagues and teams", 
                    key="leagues_btn",
                    use_container_width=True):
            st.session_state.current_page = 'leagues_teams'
            st.rerun()
    
    with col5:
        if st.button("📅\n\nCalendar\n\nView scouting calendar", 
                    key="calendar_btn",
                    use_container_width=True):
            st.session_state.current_page = 'match_calendar'
            st.rerun()

def main():
    # Initialize session state for page navigation if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # Sidebar navigation
    st.sidebar.title("⚽ Navigation")
    
    # Page selection
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Leagues & Teams", "Match Calendar", "Create Report"],
        index={"dashboard": 0, "leagues_teams": 1, "match_calendar": 2, "create_report": 3}.get(st.session_state.current_page, 0)
    )
    
    # Update session state based on selection
    if page == "Dashboard" and st.session_state.current_page != "dashboard":
        st.session_state.current_page = "dashboard"
        st.rerun()
    elif page == "Leagues & Teams" and st.session_state.current_page != "leagues_teams":
        st.session_state.current_page = "leagues_teams"
        st.rerun()
    elif page == "Match Calendar" and st.session_state.current_page != "match_calendar":
        st.session_state.current_page = "match_calendar"
        st.rerun()
    elif page == "Create Report" and st.session_state.current_page != "create_report":
        st.session_state.current_page = "create_report"
        st.rerun()
    
    # Display the appropriate page based on session state
    if st.session_state.current_page == 'dashboard':
        show_dashboard()
    elif st.session_state.current_page == 'leagues_teams':
        show_leagues_teams_page()
    elif st.session_state.current_page == 'match_calendar':
        show_calendar()
    elif st.session_state.current_page == 'create_report':
        show_create_report_page()
    else:
        st.session_state.current_page = 'dashboard'
        st.rerun()

if __name__ == "__main__":
    main()
