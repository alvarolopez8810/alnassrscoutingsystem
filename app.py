import streamlit as st
import pandas as pd
import base64
import io
from datetime import datetime, date

# Page configuration
st.set_page_config(
    page_title="FIFA U20 World Cup - Scouting Dashboard",
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
    
    # Show FIFA U20 view directly
    show_fifa_u20_view()


def show_fifa_u20_view():
    """Show FIFA U20 World Cup section with 5 tabs"""
    
    # Country flags mapping (used across multiple tabs)
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
        'México': 'mexico.svg',
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
        # Load FIFA U20 icon
        try:
            from PIL import Image
            import io
            
            icon_img = Image.open('iconfifau20.png')
            icon_img.thumbnail((40, 40))  # Resize icon
            buffered = io.BytesIO()
            
            if icon_img.mode in ('RGBA', 'LA', 'P'):
                icon_img.save(buffered, format="PNG")
                img_type = "png"
            else:
                icon_img = icon_img.convert('RGB')
                icon_img.save(buffered, format="PNG")
                img_type = "png"
            
            icon_str = base64.b64encode(buffered.getvalue()).decode()
            icon_html = f'<img src="data:image/{img_type};base64,{icon_str}" style="height:35px; vertical-align:middle; margin-right:10px;">'
        except:
            icon_html = '⚽ '  # Fallback to emoji if image fails
        
        if st.session_state.language == 'en':
            st.markdown(f"<h2 style='color: #002B5B;'>{icon_html}FIFA WORLD CUP U20</h2>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h2 style='color: #002B5B;'>{icon_html}كأس العالم تحت 20</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create 5 tabs
    if st.session_state.language == 'en':
        tabs = st.tabs([
            "📝 CREATE MATCH REPORT",
            "👤 CREATE INDIVIDUAL REPORT",
            "📊 INDIVIDUAL REPORTS",
            "🗄️ PLAYER DATABASE",
            "📈 MATCH REPORTS"
        ])
    else:
        tabs = st.tabs([
            "📝 إنشاء تقرير مباراة",
            "👤 إنشاء تقرير فردي",
            "📊 تقارير فردية",
            "🗄️ قاعدة بيانات اللاعبين",
            "📈 تقارير المباريات"
        ])
    
    # Tab 1: CREATE MATCH REPORT - Al Nassr Design
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
                    <p style="margin:0; color:#666; font-size:14px;">FIFA U20 World Cup</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # List of 24 countries
        COUNTRIES_U20 = [
            'Arabia Saudita', 'Argentina', 'Australia', 'Brasil', 'Chile', 'Colombia',
            'Corea del Sur', 'Cuba', 'Egipto', 'España', 'Estados Unidos', 'Francia',
            'Italia', 'Japón', 'Marruecos', 'México', 'Nigeria', 'Noruega',
            'Nueva Caledonia', 'Nueva Zelanda', 'Panamá', 'Paraguay', 'Sudáfrica', 'Ucrania'
        ]
        
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
                [""] + COUNTRIES_U20,
                key="fifa_home_team"
            )
        
        with col_away:
            away_team = st.selectbox(
                "✈️ Away Team" if st.session_state.language == 'en' else "✈️ الفريق الزائر",
                [""] + COUNTRIES_U20,
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
                df_players = pd.read_excel('WorldCupU20playersdata.xlsx')
                
                # Detectar nombres de columnas
                country_col_match = None
                for col in df_players.columns:
                    if col.lower() in ['país', 'pais', 'country', 'equipo', 'team']:
                        country_col_match = col
                        break
                
                position_col_match = None
                for col in df_players.columns:
                    if 'position' in col.lower() or 'posición' in col.lower():
                        position_col_match = col
                        break
                
                name_col_match = None
                for col in df_players.columns:
                    if col.lower() in ['nombre', 'name', 'player']:
                        name_col_match = col
                        break
                
                # Position order for sorting
                POSITION_ORDER = {'GK': 1, 'RB': 2, 'CB': 3, 'LB': 4, 'DM': 5, 'CM': 6, 'CAM': 7, 'RW': 8, 'LW': 9, 'ST': 10}
                
                # Get players for home team sorted by position
                home_team_df = df_players[df_players[country_col_match] == home_team].copy()
                home_team_df['pos_order'] = home_team_df[position_col_match].map(POSITION_ORDER).fillna(99)
                home_team_df = home_team_df.sort_values('pos_order')
                home_players = home_team_df[name_col_match].tolist()
                
                # Get players for away team sorted by position
                away_team_df = df_players[df_players[country_col_match] == away_team].copy()
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
                    # Get home team flag/logo
                    home_flag_file = COUNTRY_FLAGS.get(home_team, None)
                    home_flag_html = ''
                    
                    if home_flag_file:
                        try:
                            from PIL import Image
                            import io
                            
                            img = Image.open(home_flag_file)
                            img.thumbnail((40, 40))  # Resize to small
                            buffered = io.BytesIO()
                            
                            if img.mode in ('RGBA', 'LA', 'P'):
                                img.save(buffered, format="PNG")
                                img_type = "png"
                            else:
                                img = img.convert('RGB')
                                img.save(buffered, format="PNG")
                                img_type = "png"
                            
                            img_str = base64.b64encode(buffered.getvalue()).decode()
                            home_flag_html = f'<img src="data:image/{img_type};base64,{img_str}" style="height:30px; vertical-align:middle; margin-right:10px;">'
                        except:
                            home_flag_html = '🏠 '
                    else:
                        home_flag_html = '🏠 '
                    
                    st.markdown(f"### {home_flag_html}{home_team}", unsafe_allow_html=True)
                    
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
                            'potential': 1,
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
                                if selected_player != player_data.get('name', ''):
                                    st.session_state.home_match_players[idx]['name'] = selected_player
                                    
                                    # Auto-completar datos del jugador cuando se selecciona
                                    if selected_player:
                                        # 1. Buscar número anterior en reportes previos
                                        try:
                                            prev_reports = pd.read_excel('fifa_u20_player_reports.xlsx')
                                            player_prev_reports = prev_reports[prev_reports['Player Name'] == selected_player]
                                            if not player_prev_reports.empty:
                                                # Obtener el número más reciente
                                                last_number = player_prev_reports.iloc[-1]['Number']
                                                if pd.notna(last_number):
                                                    st.session_state.home_match_players[idx]['number'] = int(last_number)
                                        except:
                                            pass
                                        
                                        # 2. Buscar año de nacimiento en la base de datos
                                        try:
                                            df_players_db = pd.read_excel('WorldCupU20playersdata.xlsx')
                                            player_data_db = df_players_db[df_players_db['Nombre'].str.strip().str.lower() == selected_player.strip().lower()]
                                            if not player_data_db.empty:
                                                year_value = player_data_db.iloc[0].get('Año', '')
                                                if pd.notna(year_value):
                                                    birth_year_val = str(year_value)[:4]  # Tomar solo los primeros 4 dígitos
                                                    try:
                                                        st.session_state.home_match_players[idx]['birth_year'] = int(birth_year_val)
                                                    except:
                                                        pass
                                        except:
                                            pass
                                    
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
                                # Auto-fill position
                                default_pos = ""
                                position_index = 0
                                if selected_player:
                                    default_pos = home_player_positions.get(selected_player, "")
                                    positions_list = ["", "GK", "RB", "CB", "LB", "DM", "CM", "CAM", "RW", "LW", "ST"]
                                    if default_pos in positions_list:
                                        position_index = positions_list.index(default_pos)
                                    elif player_data.get('position') in positions_list:
                                        position_index = positions_list.index(player_data['position'])
                                
                                player_position = st.selectbox(
                                    "Position",
                                    ["", "GK", "RB", "CB", "LB", "DM", "CM", "CAM", "RW", "LW", "ST"],
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
                            
                            # Performance and Potential
                            col_perf, col_pot = st.columns(2)
                            
                            with col_perf:
                                performance = st.selectbox(
                                    "🎯 Performance (1-6)",
                                    [1, 2, 3, 4, 5, 6],
                                    index=player_data.get('performance', 1) - 1,
                                    key=f"home_p_perf_{idx}"
                                )
                                st.session_state.home_match_players[idx]['performance'] = performance
                            
                            with col_pot:
                                potential = st.selectbox(
                                    "⭐ Potential (1-6)",
                                    [1, 2, 3, 4, 5, 6],
                                    index=player_data.get('potential', 1) - 1,
                                    key=f"home_p_pot_{idx}"
                                )
                                st.session_state.home_match_players[idx]['potential'] = potential
                            
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
                    # Get away team flag/logo
                    away_flag_file = COUNTRY_FLAGS.get(away_team, None)
                    away_flag_html = ''
                    
                    if away_flag_file:
                        try:
                            from PIL import Image
                            import io
                            
                            img = Image.open(away_flag_file)
                            img.thumbnail((40, 40))  # Resize to small
                            buffered = io.BytesIO()
                            
                            if img.mode in ('RGBA', 'LA', 'P'):
                                img.save(buffered, format="PNG")
                                img_type = "png"
                            else:
                                img = img.convert('RGB')
                                img.save(buffered, format="PNG")
                                img_type = "png"
                            
                            img_str = base64.b64encode(buffered.getvalue()).decode()
                            away_flag_html = f'<img src="data:image/{img_type};base64,{img_str}" style="height:30px; vertical-align:middle; margin-right:10px;">'
                        except:
                            away_flag_html = '✈️ '
                    else:
                        away_flag_html = '✈️ '
                    
                    st.markdown(f"### {away_flag_html}{away_team}", unsafe_allow_html=True)
                    
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
                            'potential': 1,
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
                                if selected_player != player_data.get('name', ''):
                                    st.session_state.away_match_players[idx]['name'] = selected_player
                                    
                                    # Auto-completar datos del jugador cuando se selecciona
                                    if selected_player:
                                        # 1. Buscar número anterior en reportes previos
                                        try:
                                            prev_reports = pd.read_excel('fifa_u20_player_reports.xlsx')
                                            player_prev_reports = prev_reports[prev_reports['Player Name'] == selected_player]
                                            if not player_prev_reports.empty:
                                                # Obtener el número más reciente
                                                last_number = player_prev_reports.iloc[-1]['Number']
                                                if pd.notna(last_number):
                                                    st.session_state.away_match_players[idx]['number'] = int(last_number)
                                        except:
                                            pass
                                        
                                        # 2. Buscar año de nacimiento en la base de datos
                                        try:
                                            df_players_db = pd.read_excel('WorldCupU20playersdata.xlsx')
                                            player_data_db = df_players_db[df_players_db['Nombre'].str.strip().str.lower() == selected_player.strip().lower()]
                                            if not player_data_db.empty:
                                                year_value = player_data_db.iloc[0].get('Año', '')
                                                if pd.notna(year_value):
                                                    birth_year_val = str(year_value)[:4]  # Tomar solo los primeros 4 dígitos
                                                    try:
                                                        st.session_state.away_match_players[idx]['birth_year'] = int(birth_year_val)
                                                    except:
                                                        pass
                                        except:
                                            pass
                                    
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
                                # Auto-fill position
                                default_pos = ""
                                position_index = 0
                                if selected_player:
                                    default_pos = away_player_positions.get(selected_player, "")
                                    positions_list = ["", "GK", "RB", "CB", "LB", "DM", "CM", "CAM", "RW", "LW", "ST"]
                                    if default_pos in positions_list:
                                        position_index = positions_list.index(default_pos)
                                    elif player_data.get('position') in positions_list:
                                        position_index = positions_list.index(player_data['position'])
                                
                                player_position = st.selectbox(
                                    "Position",
                                    ["", "GK", "RB", "CB", "LB", "DM", "CM", "CAM", "RW", "LW", "ST"],
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
                            
                            # Performance and Potential
                            col_perf, col_pot = st.columns(2)
                            
                            with col_perf:
                                performance = st.selectbox(
                                    "🎯 Performance (1-6)",
                                    [1, 2, 3, 4, 5, 6],
                                    index=player_data.get('performance', 1) - 1,
                                    key=f"away_p_perf_{idx}"
                                )
                                st.session_state.away_match_players[idx]['performance'] = performance
                            
                            with col_pot:
                                potential = st.selectbox(
                                    "⭐ Potential (1-6)",
                                    [1, 2, 3, 4, 5, 6],
                                    index=player_data.get('potential', 1) - 1,
                                    key=f"away_p_pot_{idx}"
                                )
                                st.session_state.away_match_players[idx]['potential'] = potential
                            
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
                                    'Potential': player['potential'],
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
                                    'Potential': player['potential'],
                                    'Conclusion': player.get('conclusion', 'B - Seguir (Follow)'),
                                    'Report': player['report']
                                })
                        
                        if player_reports_list:
                            # Save directly to local Excel
                            try:
                                df_new_reports = pd.DataFrame(player_reports_list)
                                
                                # Load existing reports and append new ones
                                try:
                                    df_existing = pd.read_excel('fifa_u20_player_reports.xlsx')
                                    df_combined = pd.concat([df_existing, df_new_reports], ignore_index=True)
                                except FileNotFoundError:
                                    df_combined = df_new_reports
                                
                                # Save to Excel
                                df_combined.to_excel('fifa_u20_player_reports.xlsx', index=False)
                                
                                st.success(f"✅ Match report saved! {len(player_reports_list)} player reports added." if st.session_state.language == 'en' else f"✅ تم حفظ تقرير المباراة! تم إضافة {len(player_reports_list)} تقرير لاعب.")
                                st.balloons()
                                
                                # Clear session state
                                st.session_state.home_match_players = []
                                st.session_state.away_match_players = []
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error saving report: {e}")
                        else:
                            st.warning("⚠️ No players selected to save" if st.session_state.language == 'en' else "⚠️ لا يوجد لاعبون محددون للحفظ")
            
            except FileNotFoundError:
                st.error("❌ WorldCupU20playersdata.xlsx file not found" if st.session_state.language == 'en' else "❌ ملف WorldCupU20playersdata.xlsx غير موجود")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.info("👆 Please select both home and away teams to configure lineups" if st.session_state.language == 'en' else "👆 يرجى اختيار الفريق المحلي والزائر لإعداد التشكيلات")
    
    # Tab 2: CREATE INDIVIDUAL REPORT
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
            df_players = pd.read_excel('WorldCupU20playersdata.xlsx')
            
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
                    
                    # Scout name
                    scout_name = st.selectbox(
                        "👤 Scout Name / Nombre del Scout",
                        options=["Juan Gambero", "Alvaro Lopez", "Rafa Gil"],
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
                        df_existing_reports = pd.read_excel('fifa_u20_individual_reports.xlsx')
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
                            'Date': datetime.date.today().strftime('%Y-%m-%d'),
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
                        
                        # Save to Excel
                        try:
                            df_individual = pd.DataFrame([report_data])
                            
                            # Check if file exists
                            try:
                                df_existing = pd.read_excel('fifa_u20_individual_reports.xlsx')
                                df_combined = pd.concat([df_existing, df_individual], ignore_index=True)
                            except FileNotFoundError:
                                df_combined = df_individual
                            
                            df_combined.to_excel('fifa_u20_individual_reports.xlsx', index=False)
                            
                            st.success("✅ Individual report saved successfully!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Error saving report: {e}")
        
        except FileNotFoundError:
            st.error("❌ WorldCupU20playersdata.xlsx not found. Please add the player database file.")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Tab 3: INDIVIDUAL REPORTS (View saved reports)
    with tabs[2]:
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
            df_individual_reports = pd.read_excel('fifa_u20_individual_reports.xlsx')
            
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
                
                with col_f1:
                    scouts_filter = ['All Scouts'] + sorted(df_individual_reports['Scout'].dropna().unique().tolist())
                    selected_scout_filter = st.selectbox("👤 Scout", scouts_filter, key="ind_reports_scout_filter")
                
                with col_f2:
                    # Filtrar equipos según el scout seleccionado
                    if selected_scout_filter != 'All Scouts':
                        available_teams = df_individual_reports[df_individual_reports['Scout'] == selected_scout_filter]['Team'].unique()
                    else:
                        available_teams = df_individual_reports['Team'].unique()
                    teams_filter = ['All Teams'] + sorted(available_teams.tolist())
                    selected_team_filter = st.selectbox("🌍 Team", teams_filter, key="ind_reports_team_filter")
                
                with col_f3:
                    # Filtrar jugadores según scout y equipo seleccionados
                    filtered_for_players = df_individual_reports.copy()
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
                
                # Apply filters
                filtered_reports = df_individual_reports.copy()
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
                    filename_base="fifa_u20_individual_reports",
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
                        
                        # Calcular medias
                        avg_rendimiento = player_reports['Rendimiento'].mean()
                        avg_potencial = player_reports['Potencial'].mean()
                        
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
                    with st.expander(
                        f"👤 {report['Player']} ({report['Team']}) | {report['Conclusion']} | 📅 {report['Date']} | 👤 Scout: {scout_name}",
                        expanded=False  # Colapsado por defecto
                    ):
                        # === CSS FINAL LIMPIO Y MINIMALISTA ===
                        st.markdown("""
                            <style>
                            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
                            body { background-color: #fafafa; font-family: 'Inter', sans-serif; }
                            
                            .player-photo-final { 
                                width: 120px; 
                                height: 120px; 
                                border-radius: 50%; 
                                border: 3px solid #FFD700; 
                                object-fit: cover; 
                                margin: 0 auto; 
                                display: block;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                            }
                            .player-name-final { 
                                font-size: 32px; 
                                font-weight: 700; 
                                color: #1B2845; 
                                text-align: center; 
                                margin: 15px 0 8px 0; 
                            }
                            .player-subtitle-final { 
                                font-size: 15px; 
                                color: #6c757d; 
                                text-align: center; 
                                margin-bottom: 0;
                            }
                            
                            .metric-card-final { 
                                background: white; 
                                padding: 25px 20px; 
                                border-radius: 12px; 
                                box-shadow: 0 4px 20px rgba(0,0,0,0.06); 
                                text-align: center;
                                transition: transform 0.3s ease, box-shadow 0.3s ease;
                                height: 100%;
                            }
                            .metric-card-final:hover {
                                transform: translateY(-3px);
                                box-shadow: 0 6px 25px rgba(0,0,0,0.12);
                            }
                            .metric-number-final { 
                                font-size: 48px; 
                                font-weight: 700; 
                                color: #1B2845; 
                                line-height: 1; 
                                margin-bottom: 10px;
                            }
                            .metric-label-final { 
                                font-size: 12px; 
                                color: #999; 
                                text-transform: uppercase; 
                                letter-spacing: 2px; 
                                margin-bottom: 15px;
                                font-weight: 600;
                            }
                            .stars-final { 
                                font-size: 20px; 
                                display: flex; 
                                justify-content: center; 
                                gap: 5px;
                            }
                            .star-gold { color: #FFD700; filter: drop-shadow(0 2px 3px rgba(255,215,0,0.3)); }
                            .star-gray { color: #e9ecef; }
                            
                            .secondary-info-final {
                                background: white;
                                padding: 20px;
                                border-radius: 12px;
                                box-shadow: 0 4px 20px rgba(0,0,0,0.06);
                                display: flex;
                                justify-content: center;
                                gap: 30px;
                                flex-wrap: wrap;
                                margin: 40px 0;
                            }
                            .secondary-info-final span {
                                font-size: 14px;
                                color: #495057;
                            }
                            
                            .tech-comment-final {
                                background: #f8f9fa;
                                padding: 25px;
                                border-radius: 12px;
                                border-left: 4px solid #FFD700;
                                box-shadow: 0 2px 15px rgba(0,0,0,0.05);
                                height: 100%;
                                display: flex;
                                align-items: center;
                            }
                            .tech-comment-final p {
                                font-style: italic;
                                color: #495057;
                                font-size: 16px;
                                margin: 0;
                                line-height: 1.6;
                            }
                            
                            .conclusion-final {
                                background: #f8f9fa;
                                padding: 25px 35px;
                                border-radius: 12px;
                                box-shadow: 0 2px 15px rgba(0,0,0,0.05);
                                height: 100%;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                text-align: center;
                            }
                            .conclusion-final p {
                                font-size: 28px;
                                font-weight: 700;
                                text-transform: uppercase;
                                margin: 0;
                                line-height: 1.3;
                            }
                            .conclusion-green { color: #28a745; }
                            .conclusion-blue { color: #1B2845; }
                            .conclusion-orange { color: #ff8c00; }
                            
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
                        
                        # === HEADER SECTION (2 COLUMNAS) ===
                        col_left, col_right = st.columns([250, 1000], gap="large")
                        
                        # COLUMNA IZQUIERDA: Foto + Nombre + Subtítulo
                        with col_left:
                            # Foto circular
                            if report.get('Photo') and report['Photo']:
                                try:
                                    from PIL import Image
                                    import io
                                    img = Image.open(report['Photo'])
                                    # Convertir a base64 para aplicar clase CSS
                                    buffered = io.BytesIO()
                                    if img.mode in ('RGBA', 'LA', 'P'):
                                        img.save(buffered, format="PNG")
                                    else:
                                        img = img.convert('RGB')
                                        img.save(buffered, format="PNG")
                                    img_str = base64.b64encode(buffered.getvalue()).decode()
                                    st.markdown(f'<img src="data:image/png;base64,{img_str}" class="player-photo-final">', unsafe_allow_html=True)
                                except:
                                    # Usar logo Al Nassr como placeholder
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
                                        st.markdown(f'<img src="data:image/png;base64,{logo_str}" class="player-photo-final">', unsafe_allow_html=True)
                                    except:
                                        st.markdown('<div style="width:120px; height:120px; border-radius:50%; border:3px solid #FFD700; display:flex; align-items:center; justify-content:center; margin:0 auto; background:#f0f0f0; font-size:50px;">👤</div>', unsafe_allow_html=True)
                            else:
                                # Usar logo Al Nassr como placeholder
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
                                    st.markdown(f'<img src="data:image/png;base64,{logo_str}" class="player-photo-final">', unsafe_allow_html=True)
                                except:
                                    st.markdown('<div style="width:120px; height:120px; border-radius:50%; border:3px solid #FFD700; display:flex; align-items:center; justify-content:center; margin:0 auto; background:#f0f0f0; font-size:50px;">👤</div>', unsafe_allow_html=True)
                            
                            # Nombre
                            st.markdown(f'<p class="player-name-final">{report["Player"]}</p>', unsafe_allow_html=True)
                            
                            # Subtítulo con posición, año, país y bandera
                            birth_year = str(report['Birth Date'])[:4] if report.get('Birth Date') else 'N/A'
                            position = report.get('Position', 'N/A')
                            team = report['Team']
                            
                            # Get country flag
                            flag_html = ''
                            flag_file = COUNTRY_FLAGS.get(team, None)
                            if flag_file:
                                try:
                                    from PIL import Image
                                    import io
                                    flag_img = Image.open(flag_file)
                                    flag_img.thumbnail((20, 20))
                                    buffered = io.BytesIO()
                                    if flag_img.mode in ('RGBA', 'LA', 'P'):
                                        flag_img.save(buffered, format="PNG")
                                    else:
                                        flag_img = flag_img.convert('RGB')
                                        flag_img.save(buffered, format="PNG")
                                    flag_str = base64.b64encode(buffered.getvalue()).decode()
                                    flag_html = f' <img src="data:image/png;base64,{flag_str}" style="height:16px; vertical-align:middle;">'
                                except:
                                    pass
                            
                            st.markdown(f'<p class="player-subtitle-final">{position} • {birth_year} • {team}{flag_html}</p>', unsafe_allow_html=True)
                        
                        # COLUMNA DERECHA: Grid de 3 métricas
                        with col_right:
                            col_m1, col_m2, col_m3 = st.columns(3)
                            
                            # Métrica 1: Rendimiento
                            with col_m1:
                                rendimiento = int(report['Rendimiento'])
                                stars_html = ''.join([f'<span class="star-gold">⭐</span>' for _ in range(rendimiento)]) + ''.join([f'<span class="star-gray">☆</span>' for _ in range(6 - rendimiento)])
                                st.markdown(f"""
                                    <div class="metric-card-final animate-fade-in">
                                        <div class="metric-number-final">{rendimiento}</div>
                                        <div class="metric-label-final">Rendimiento</div>
                                        <div class="stars-final">{stars_html}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            # Métrica 2: Potencial
                            with col_m2:
                                potencial = int(report['Potencial'])
                                stars_html = ''.join([f'<span class="star-gold">⭐</span>' for _ in range(potencial)]) + ''.join([f'<span class="star-gray">☆</span>' for _ in range(6 - potencial)])
                                st.markdown(f"""
                                    <div class="metric-card-final animate-fade-in">
                                        <div class="metric-number-final">{potencial}</div>
                                        <div class="metric-label-final">Potencial</div>
                                        <div class="stars-final">{stars_html}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            # Métrica 3: Perfil
                            with col_m3:
                                perfil_val = report['Perfil']
                                if isinstance(perfil_val, str) and '-' in perfil_val:
                                    perfil_num = int(perfil_val.split(' - ')[0])
                                else:
                                    perfil_num = int(perfil_val)
                                stars_html = ''.join([f'<span class="star-gold">⭐</span>' for _ in range(perfil_num)]) + ''.join([f'<span class="star-gray">☆</span>' for _ in range(6 - perfil_num)])
                                st.markdown(f"""
                                    <div class="metric-card-final animate-fade-in">
                                        <div class="metric-number-final">{perfil_num}</div>
                                        <div class="metric-label-final">Perfil</div>
                                        <div class="stars-final">{stars_html}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        # === INFORMACIÓN SECUNDARIA ===
                        contract = report.get('Contract', 'N/A')
                        agent = report.get('Agent', 'N/A')
                        phone = report.get('Agent Phone', 'N/A')
                        report_date = report.get('Date', 'N/A')
                        scout = report.get('Scout', 'N/A')
                        
                        st.markdown(f"""
                            <div class="secondary-info-final animate-fade-in">
                                <span>📄 {contract}</span>
                                <span>🤝 {agent}</span>
                                <span>📞 {phone}</span>
                                <span>📅 {report_date}</span>
                                <span>👤 {scout}</span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # === SECCIÓN INFERIOR: COMENTARIO TÉCNICO Y CONCLUSIÓN (2 COLUMNAS) ===
                        col_comment, col_conclusion = st.columns(2)
                        
                        # COLUMNA IZQUIERDA: Comentario técnico
                        with col_comment:
                            tech_comment = report.get('Technical Comment', None)
                            if tech_comment and str(tech_comment) != 'nan' and str(tech_comment).strip():
                                st.markdown(f"""
                                    <div class="tech-comment-final animate-fade-in">
                                        <p>{tech_comment}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                    <div class="tech-comment-final animate-fade-in">
                                        <p style="color: #999;">No technical comment available.</p>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        # COLUMNA DERECHA: Conclusión
                        with col_conclusion:
                            conclusion = report.get('Conclusion', '')
                            
                            # Determinar color del texto según conclusión
                            if conclusion.startswith('A'):
                                conclusion_class = 'conclusion-green'
                            elif conclusion.startswith('B+'):
                                conclusion_class = 'conclusion-blue'
                            elif conclusion.startswith('B') and not conclusion.startswith('B+'):
                                conclusion_class = 'conclusion-orange'
                            else:
                                conclusion_class = 'conclusion-blue'  # Default
                            
                            st.markdown(f"""
                                <div class="conclusion-final animate-fade-in">
                                    <p class="{conclusion_class}">{conclusion}</p>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("🔍 No individual reports found. Create one in the CREATE INDIVIDUAL REPORT tab.")
        
        except FileNotFoundError:
            st.info("📊 No individual reports yet. Create your first report!")
        except Exception as e:
            st.error(f"Error loading reports: {e}")
    
    # Tab 4: PLAYER DATABASE
    with tabs[3]:
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
            st.markdown(f"<h3>{logo_title_html} Player Database - FIFA U20 World Cup</h3>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h3>{logo_title_html} قاعدة بيانات اللاعبين - كأس العالم تحت 20</h3>", unsafe_allow_html=True)
        
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
        
        # Load player data
        try:
            df_players = pd.read_excel('WorldCupU20playersdata.xlsx')
            
            # Detectar nombres de columnas automáticamente
            # Buscar columna de país/equipo
            country_col = None
            for col in df_players.columns:
                if col.lower() in ['país', 'pais', 'paíós', 'country', 'equipo', 'team']:
                    country_col = col
                    break
            
            # Buscar columna de posición
            position_col = None
            for col in df_players.columns:
                if 'position' in col.lower() or 'posición' in col.lower():
                    position_col = col
                    break
            
            # Buscar columna de nombre
            name_col = None
            for col in df_players.columns:
                if col.lower() in ['nombre', 'name', 'player']:
                    name_col = col
                    break
            
            # Verificar que existan las columnas necesarias
            if not country_col or not position_col or not name_col:
                st.error("⚠️ No se encontraron las columnas necesarias en el Excel. Asegúrate de que existan: País/Country, Position, Nombre/Name")
                raise ValueError("Columnas necesarias no encontradas")
        
        except Exception as e:
            st.error(f"❌ Error al cargar datos de jugadores: {str(e)}")
            df_players = pd.DataFrame()
            
        # Load match reports from local Excel
        try:
            df_reports = pd.read_excel('fifa_u20_player_reports.xlsx')
        except FileNotFoundError:
            df_reports = pd.DataFrame()
        except Exception as e:
            df_reports = pd.DataFrame()
        
        # Try to load individual reports
        try:
            df_individual_reports = pd.read_excel('fifa_u20_individual_reports.xlsx')
        except FileNotFoundError:
            df_individual_reports = pd.DataFrame()
        except Exception as e:
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
        col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
        
        with col_filter1:
            # Search by player name
            search_player = st.text_input(
                "🔍 Search Player" if st.session_state.language == 'en' else "🔍 ابحث عن لاعب",
                placeholder="Enter player name..." if st.session_state.language == 'en' else "أدخل اسم اللاعب...",
                key="fifa_u20_search_player"
            )
        
        with col_filter2:
            # Position filter
            all_positions = ['All Positions'] + sorted(df_players[position_col].dropna().unique().tolist())
            selected_position = st.selectbox(
                "⚽ Position" if st.session_state.language == 'en' else "⚽ المركز",
                all_positions,
                key="fifa_u20_position_filter"
            )
        
        with col_filter3:
            # Country filter
            all_countries = ['All Teams'] + sorted(df_players[country_col].unique().tolist())
            selected_country = st.selectbox(
                "🌍 Team" if st.session_state.language == 'en' else "🌍 الفريق",
                all_countries,
                key="fifa_u20_country_filter"
            )
        
        with col_filter4:
            # Conclusion filter
            conclusion_options = ['Todas', 'A - Firmar', 'B+ - Seguir para Firmar', 'B - Seguir']
            selected_conclusion = st.selectbox(
                "🎯 Conclusión",
                conclusion_options,
                key="fifa_u20_conclusion_filter"
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
        
        if selected_country != 'All Teams':
            filtered_df = filtered_df[filtered_df[country_col] == selected_country]
        
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
            selected_country != 'All Teams' or
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
            st.metric("🌍 Teams", filtered_df[country_col].nunique() if not filtered_df.empty else 0)
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
                filename_base="fifa_u20_player_database",
                label_prefix="Descargar / Download"
            )
            st.markdown("---")
        
        if filtered_df.empty:
            if not st.session_state.show_all_players and not has_active_filters:
                st.info("👥 Haz clic en 'Mostrar todos' o usa los filtros para ver los jugadores" if st.session_state.language == 'en' else "👥 انقر على 'إظهار الكل' أو استخدم الفلاتر لمشاهدة اللاعبين")
            else:
                st.warning("❌ No se encontraron jugadores con los filtros seleccionados" if st.session_state.language == 'en' else "❌ لا يوجد لاعبون بالفلاتر المحددة")
        else:
            # Group by country/team
            for country in sorted(filtered_df[country_col].unique()):
                country_players = filtered_df[filtered_df[country_col] == country]
                
                # Country header with flag/logo image using PIL
                flag_file = COUNTRY_FLAGS.get(country, None)
                flag_html = ''
                
                if flag_file:
                    try:
                        # Use PIL to open and encode image
                        from PIL import Image
                        import io
                        
                        img = Image.open(flag_file)
                        buffered = io.BytesIO()
                        
                        # Convert to RGB if necessary and save as PNG
                        if img.mode in ('RGBA', 'LA', 'P'):
                            # Keep transparency
                            img.save(buffered, format="PNG")
                            img_type = "png"
                        else:
                            img = img.convert('RGB')
                            img.save(buffered, format="PNG")
                            img_type = "png"
                        
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        flag_html = f'<img src="data:image/{img_type};base64,{img_str}" style="height:40px; vertical-align:middle; margin-right:10px;">'
                    except Exception as e:
                        flag_html = '🏴 '
                else:
                    flag_html = '🏴 '
                
                # Count players with match reports in this team
                team_players_with_match_reports = 0
                if not df_reports.empty:
                    team_players_with_match_reports = country_players[name_col].isin(df_reports['Player Name']).sum()
                
                # Count players with individual reports in this team
                team_players_with_individual_reports = 0
                if not df_individual_reports.empty:
                    team_players_with_individual_reports = country_players[name_col].isin(df_individual_reports['Player']).sum()
                
                # Display country header
                st.markdown(
                    f'<div style="background-color: #002B5B; color: white; padding: 1rem; border-radius: 8px; margin: 1rem 0; font-weight: bold; font-size: 1.2rem;">{flag_html}{country} U20 ({len(country_players)} players | ⚽ {team_players_with_match_reports} match reports | 📋 {team_players_with_individual_reports} individual reports)</div>',
                    unsafe_allow_html=True
                )
                
                # Display players as expandable cards within this team
                for idx, player in country_players.iterrows():
                    player_name = player[name_col]
                    player_position = player.get(position_col, 'N/A')
                    player_team = player[country_col]
                    player_age = player.get('Edad', 'N/A')
                    player_club = player.get('Equipo', 'N/A')
                    
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
                                                    <div style="color: #FFC60A; font-size: 12px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px;">TEAM</div>
                                                    <div style="color: white; font-size: 24px; font-weight: 600;">{player.get('Equipo', 'N/A')}</div>
                                                </div>
                                                <div>
                                                    <div style="color: #FFC60A; font-size: 12px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px;">AGE</div>
                                                    <div style="color: white; font-size: 24px; font-weight: 600;">{player_age}</div>
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
                                        import time
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
    
    # Tab 5: MATCH REPORTS - Al Nassr Professional Dashboard
    with tabs[4]:
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
        st.markdown("<h3 style='text-align: center; color: #666;'>FIFA U20 World Cup</h3>", unsafe_allow_html=True)
        
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
        
        # Load match reports from local Excel
        try:
            df_reports = pd.read_excel('fifa_u20_player_reports.xlsx')
        except FileNotFoundError:
            df_reports = pd.DataFrame()
        except Exception as e:
            df_reports = pd.DataFrame()
        
        # Load player birth year data from WorldCupU20playersdata.xlsx
        try:
            df_players_data = pd.read_excel('WorldCupU20playersdata.xlsx')
            
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
            total_teams = len(set([team.strip() for match in df_reports['Match'].unique() for team in match.split(' vs ') if ' vs ' in match]))
            
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
            st.markdown("<h3 style='color: #1a2332;'>🔍 FILTROS</h3>", unsafe_allow_html=True)
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                filter_scout = st.selectbox(
                    "🔍 Filter by Scout" if st.session_state.language == 'en' else "🔍 تصفية حسب الكشاف",
                    [""] + sorted(df_reports['Scout'].dropna().unique().tolist()),
                    key="filter_scout_match_reports"
                )
            
            with col_f2:
                filter_phase = st.selectbox(
                    "🏆 Filter by Phase" if st.session_state.language == 'en' else "🏆 تصفية حسب المرحلة",
                    [""] + sorted(df_reports['Phase'].dropna().unique().tolist()),
                    key="filter_phase_match_reports"
                )
            
            with col_f3:
                filter_conclusion = st.selectbox(
                    "✅ Filter by Conclusion" if st.session_state.language == 'en' else "✅ تصفية حسب الخلاصة",
                    ["", "A - Firmar (Sign)", "B+ - Seguir para Firmar (Follow to Sign)", "B - Seguir (Follow)"],
                    key="filter_conclusion_match_reports"
                )
            
            # Apply filters
            filtered_reports = df_reports.copy()
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
                    filename_base="fifa_u20_match_reports",
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
                    team1_flag_html = ''
                    team2_flag_html = ''
                    
                    for team_name, var_name in [(team1, 'team1_flag_html'), (team2, 'team2_flag_html')]:
                        flag_file = COUNTRY_FLAG_MAP.get(team_name, None)
                        if flag_file:
                            try:
                                from PIL import Image
                                import io
                                flag_img = Image.open(flag_file)
                                flag_img.thumbnail((24, 24))
                                buffered = io.BytesIO()
                                if flag_img.mode in ('RGBA', 'LA', 'P'):
                                    flag_img.save(buffered, format="PNG")
                                else:
                                    flag_img = flag_img.convert('RGB')
                                    flag_img.save(buffered, format="PNG")
                                flag_str = base64.b64encode(buffered.getvalue()).decode()
                                flag_html = f'<img src="data:image/png;base64,{flag_str}" style="height: 20px; margin-right: 8px; vertical-align: middle;">'
                                if var_name == 'team1_flag_html':
                                    team1_flag_html = flag_html
                                else:
                                    team2_flag_html = flag_html
                            except Exception as e:
                                # Show emoji flag as fallback
                                if var_name == 'team1_flag_html':
                                    team1_flag_html = '🏁 '
                                else:
                                    team2_flag_html = '🏁 '
                        else:
                            # No flag file found in mapping
                            if var_name == 'team1_flag_html':
                                team1_flag_html = '🏁 '
                            else:
                                team2_flag_html = '🏁 '
                    
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
                            
                            # Load team flag for section header
                            team_flag_html = ''
                            flag_file = COUNTRY_FLAG_MAP.get(team_name, None)
                            if flag_file:
                                try:
                                    from PIL import Image
                                    import io
                                    team_flag_img = Image.open(flag_file)
                                    team_flag_img.thumbnail((24, 24))
                                    buffered_team = io.BytesIO()
                                    if team_flag_img.mode in ('RGBA', 'LA', 'P'):
                                        team_flag_img.save(buffered_team, format="PNG")
                                    else:
                                        team_flag_img = team_flag_img.convert('RGB')
                                        team_flag_img.save(buffered_team, format="PNG")
                                    team_flag_str = base64.b64encode(buffered_team.getvalue()).decode()
                                    team_flag_html = f'<img src="data:image/png;base64,{team_flag_str}" style="height: 20px; margin-right: 8px; vertical-align: middle;">'
                                except:
                                    team_flag_html = '🏁 '
                            else:
                                team_flag_html = '🏁 '
                            
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
                                
                                # Load player's team flag
                                flag_file = COUNTRY_FLAG_MAP.get(str(player_team).strip(), None)
                                if flag_file:
                                    try:
                                        from PIL import Image
                                        import io
                                        flag_img = Image.open(flag_file)
                                        flag_img.thumbnail((24, 24))
                                        buffered = io.BytesIO()
                                        if flag_img.mode in ('RGBA', 'LA', 'P'):
                                            flag_img.save(buffered, format="PNG")
                                        else:
                                            flag_img = flag_img.convert('RGB')
                                            flag_img.save(buffered, format="PNG")
                                        flag_str = base64.b64encode(buffered.getvalue()).decode()
                                        flag_html = f'<img src="data:image/png;base64,{flag_str}" style="height: 18px; margin-right: 6px; vertical-align: middle;">'
                                    except:
                                        flag_html = ''
                                else:
                                    flag_html = ''
                                
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
                                    
                                    # Create editable fields
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
                                    
                                    # Save button
                                    if st.button("💾 GUARDAR CAMBIOS", key=f"save_{player_key}", type="primary"):
                                        try:
                                            # Load current Excel data
                                            df_all_reports = pd.read_excel('fifa_u20_player_reports.xlsx')
                                            
                                            # Find the exact row to update using multiple criteria
                                            mask = (
                                                (df_all_reports['Scout'] == scout) &
                                                (df_all_reports['Match'] == match_name) &
                                                (df_all_reports[player_col] == player_name)
                                            )
                                            
                                            # Update the values
                                            df_all_reports.loc[mask, 'Performance'] = new_performance
                                            df_all_reports.loc[mask, 'Potential'] = new_potential
                                            df_all_reports.loc[mask, 'Conclusion'] = new_conclusion
                                            df_all_reports.loc[mask, 'Report'] = new_report
                                            
                                            # Save back to Excel
                                            df_all_reports.to_excel('fifa_u20_player_reports.xlsx', index=False)
                                            
                                            st.success("✅ Informe actualizado exitosamente!")
                                            st.session_state[edit_key] = False
                                            
                                            # Wait a moment and reload
                                            import time
                                            time.sleep(1)
                                            st.rerun()
                                            
                                        except Exception as e:
                                            st.error(f"❌ Error al guardar: {e}")
                                    
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
        
        st.markdown(f"### {logo_login_html} FIFA U20 Scouting", unsafe_allow_html=True)
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
        st.info("🔒 Secure access for FIFA U20 scouts only")

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
